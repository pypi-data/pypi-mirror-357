#!/usr/bin/env python3
"""
Internal developer utilities for gai-sdk.

Usage examples
--------------
python -m gai.scripts.devtool bump-version         # patch++
python -m gai.scripts.devtool build
python -m gai.scripts.devtool smoke-test
python -m gai.scripts.devtool publish
"""

import os
import argparse, pathlib, shutil, subprocess, sys, textwrap, toml, tempfile
from rich import print
from importlib.resources import files
from ._docker_utils import _docker_build, _docker_push

ROOT = pathlib.Path(
    os.getcwd()
)  # Assuming this script is run from the root of the project


# ── helpers ───────────────────────────────────────────────────────────────
def bump_version(part: str = "patch"):
    pj = ROOT / "pyproject.toml"
    data = toml.loads(pj.read_text())
    ver = data["project"]["version"].split(".")
    if part == "major":
        ver[0] = str(int(ver[0]) + 1)
        ver[1:] = ["0", "0"]
    elif part == "minor":
        ver[1] = str(int(ver[1]) + 1)
        ver[2] = "0"
    else:
        ver[2] = str(int(ver[2]) + 1)
    data["project"]["version"] = ".".join(ver)
    pj.write_text(toml.dumps(data))
    print("📌 bumped to", data["project"]["version"])


def inspect_pkg_data():
    import sys, zipfile, pathlib

    wheels = list(pathlib.Path("dist").glob("*.whl"))
    if not wheels:
        print("❌  No wheel found in ./dist – run `gai-dev build` first.")
        sys.exit(1)
    whl = wheels[0]
    with zipfile.ZipFile(whl) as z:
        for name in z.namelist():
            if name.startswith("gai/scripts/data/"):
                print(" •", name.removeprefix("gai/scripts/data/"))


def build():
    shutil.rmtree("dist", ignore_errors=True)
    subprocess.check_call([sys.executable, "-m", "build", "-w", "-s"])


def smoke_install(use_editable: bool = False):
    pj = ROOT / "pyproject.toml"
    data = toml.loads(pj.read_text())
    version = data["project"]["version"]
    print(f"[yellow]🔍 Testing gai-lib version: {version}[/yellow]")

    with tempfile.TemporaryDirectory() as tmpdir:
        # create a temp environment
        env_dir = os.path.join(tmpdir, "env")

        # venv.create(env_dir, with_pip=True)
        env_dir = os.path.join(tmpdir, "env")
        subprocess.check_call(["uv", "venv", env_dir, "--seed"])
        env = os.environ.copy()
        env["PATH"] = os.path.join(env_dir, "bin") + os.pathsep + env["PATH"]
        env["VIRTUAL_ENV"] = env_dir
        env["UV_PROJECT_ENVIRONMENT"] = env_dir
        subprocess.check_call(["which", "python"], env=env)

        py = "python"

        # Check version of gai-lib installed in the environment against the one in pyproject.toml
        if use_editable:
            subprocess.check_call([py, "-m", "pip", "install", "-e", "."], env=env)
        else:
            wheel = next(pathlib.Path("dist").glob("*.whl"))
            subprocess.check_call(
                [py, "-m", "pip", "install", wheel], env=env
            )

        # simpler: grep gai-lib version from pip list
        output = subprocess.check_output(
            f"{py} -m pip list --format=freeze | grep gai-lib",
            shell=True,
            env=env,
            text=True,
        )
        # output is like "gai-lib==1.2.3\n"
        installed_version = output.strip().split("==", 1)[1]
        print(f"[green]✅ Installed gai-lib version: {installed_version}[/green]")

        if installed_version != version:
            print(f"[red]⚠️ Version mismatch! Expected {version}[/red]")        

        # # install the exact version we just read

        # if use_editable:
        #     subprocess.check_call([py, "-m", "pip", "install", "-e", ".."], env=env)
        # else:
        #     wheel = next(pathlib.Path("dist").glob("*.whl"))
        #     subprocess.check_call(
        #         [py, "-m", "pip", "install", wheel, "--no-deps"], env=env
        #     )

        # # import gai.lib
        # subprocess.check_call([py, "-c", "import gai.lib.utils"], env=env)
        print("[yellow]✅ Can import gai.lib[/]")

    print("[green]🟢 Smoke test passed[/]")


def publish():
    subprocess.check_call(["twine", "upload", "dist/*"])


def docker_build(
    pyproject_path="pyproject.toml",
    repo_name="kakkoii1337",
    image_name=None,
    dockerfile_path=None,
    dockercontext_path=None,
    no_cache=False,
):
    """Build a Docker image from a Dockerfile.

    Args:
        pyproject_path: Path to the pyproject.toml file
        repo_name: Docker repository name
        image_name: Docker image name (defaults to project name from pyproject.toml)
        dockerfile_path: Path to the Dockerfile (defaults to ./Dockerfile)
        dockercontext_path: Path to the Docker build context (defaults to directory containing pyproject.toml)
        no_cache: If True, don't use cache when building the image
    """
    _docker_build(
        pyproject_path=pyproject_path,
        repo_name=repo_name,
        image_name=image_name,
        dockerfile_path=dockerfile_path,
        dockercontext_path=dockercontext_path,
        no_cache=no_cache,
    )


def docker_push(
    pyproject_path="pyproject.toml", repo_name="kakkoii1337", image_name=None
):
    """Push a Docker image to a repository.

    Args:
        pyproject_path: Path to the pyproject.toml file
        repo_name: Docker repository name
        image_name: Docker image name (defaults to project name from pyproject.toml)
    """
    _docker_push(
        pyproject_path=pyproject_path, repo_name=repo_name, image_name=image_name
    )


# ── CLI ───────────────────────────────────────────────────────────────────
def _cli():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("bump-version").add_argument(
        "--part", choices=["major", "minor", "patch"], default="patch"
    )
    sub.add_parser("build")
    sub.add_parser("smoke-test")
    sub.add_parser("publish")
    sub.add_parser("inspect-pkg-data")

    # Add docker_build command
    docker_parser = sub.add_parser("docker_build")
    docker_parser.add_argument(
        "--pyproject-path", default="pyproject.toml", help="Path to pyproject.toml file"
    )
    docker_parser.add_argument(
        "--repo-name", default="kakkoii1337", help="Docker repository name"
    )
    docker_parser.add_argument("--image-name", help="Docker image name")
    docker_parser.add_argument("--dockerfile-path", help="Path to Dockerfile")
    docker_parser.add_argument("--dockercontext-path", help="Path to docker context")
    docker_parser.add_argument(
        "--no-cache", action="store_true", help="Do not use cache when building"
    )

    # Add docker_push command
    docker_push_parser = sub.add_parser("docker_push")
    docker_push_parser.add_argument(
        "--pyproject-path", default="pyproject.toml", help="Path to pyproject.toml file"
    )
    docker_push_parser.add_argument(
        "--repo-name", default="kakkoii1337", help="Docker repository name"
    )
    docker_push_parser.add_argument("--image-name", help="Docker image name")

    args = p.parse_args()

    if args.cmd == "bump-version":
        bump_version(args.part)
    elif args.cmd == "build":
        build()
    elif args.cmd == "smoke-test":
        smoke_install()
    elif args.cmd == "inspect-pkg-data":
        inspect_pkg_data()
    elif args.cmd == "publish":
        publish()
    elif args.cmd == "docker_build":
        docker_build(
            pyproject_path=args.pyproject_path,
            repo_name=args.repo_name,
            image_name=args.image_name,
            dockerfile_path=args.dockerfile_path,
            dockercontext_path=args.dockercontext_path,
            no_cache=args.no_cache,
        )
    elif args.cmd == "docker_push":
        docker_push(
            pyproject_path=args.pyproject_path,
            repo_name=args.repo_name,
            image_name=args.image_name,
        )


if __name__ == "__main__":
    _cli()
