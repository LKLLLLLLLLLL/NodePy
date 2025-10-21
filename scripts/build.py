import subprocess
import shutil
from pathlib import Path
from typing import List


def _compose_prefix() -> List[str]:
    """Return the command prefix for invoking docker compose.

    Prefer the standalone `docker-compose` binary if present, otherwise fall
    back to the `docker compose` subcommand.
    """
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    # Use Docker CLI compose subcommand (docker compose ...) if available
    if shutil.which("docker"):
        return ["docker", "compose"]
    raise RuntimeError("Neither 'docker-compose' nor 'docker' found in PATH")

def _npm_prefix() -> List[str]:
    """ Return the command prefix for invoking npm. """
    npm_prefix = shutil.which("npm")
    if npm_prefix:
        return [npm_prefix]
    raise RuntimeError("'npm' not found in PATH")

def build() -> None:
    """Build frontend assets and Docker images."""
    project_root = Path(__file__).resolve().parent.parent

    # 1. Build frontend
    print("🔨 Building frontend...")
    client_dir = project_root / "client"
    npm = _npm_prefix()
    cmd = npm + ["install"]
    subprocess.run(cmd, cwd=client_dir, check=True)
    cmd = npm + ["run", "build"]
    subprocess.run(cmd, cwd=client_dir, check=True)

    # 2. Build Docker images
    print("🐳 Building Docker images...")
    infra_dir = project_root / "infra"
    compose = _compose_prefix()
    cmd = compose + ["-f", "docker-compose.yml", "-p", "nodepy", "build"]
    try:
        subprocess.run(cmd, cwd=infra_dir, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Error: docker compose build failed with exit code {exc.returncode}")
        raise

    print("✅ Build completed successfully!")


def start_dev() -> None:
    """Build assets and start development services in detached mode.

    Note: frontend dev server is expected to be started separately by frontend
    developers (e.g. `cd client && npm run dev`).
    """
    build()
    print("🚀 Starting backend services (detached). Frontend dev should be run manually: cd client && npm run dev")
    infra_dir = Path(__file__).resolve().parent.parent / "infra"
    compose = _compose_prefix()
    cmd = compose + ["-f", "docker-compose.yml", "-p", "nodepy", "up", "-d"]
    subprocess.run(cmd, cwd=infra_dir, check=True)


def start_prod() -> None:
    """Build assets and start production services."""
    build()
    print("🚀 Starting production environment...")
    infra_dir = Path(__file__).resolve().parent.parent / "infra"
    compose = _compose_prefix()
    cmd = compose + ["-f", "docker-compose.prod.yml", "-p", "nodepy", "up"]
    subprocess.run(cmd, cwd=infra_dir, check=True)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m scripts.build <command>")
        print("Commands: build, dev, prod")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "build":
        build()
    elif cmd == "dev":
        start_dev()
    elif cmd == "prod":
        start_prod()
    else:
        print("Unknown command")