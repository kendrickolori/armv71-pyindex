#!/usr/bin/env python3
"""Build wheels for packages listed in packages.toml"""

import toml
import subprocess
import os
from pathlib import Path

def build_wheel_in_docker(package_name, version):
    """Build a wheel using Docker with ARM emulation"""
    
    # Create a temporary Dockerfile
    dockerfile_content = f"""
FROM arm32v7/python:3.11-slim

RUN apt-get update && apt-get install -y \\
    gcc g++ make \\
    libffi-dev libssl-dev \\
    libjpeg-dev zlib1g-dev \\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip wheel setuptools

WORKDIR /build
CMD pip wheel {package_name}=={version} --no-deps -w /output
"""
    
    Path("Dockerfile.build").write_text(dockerfile_content)
    
    # Build the Docker image
    print(f"Building {package_name}=={version}...")
    subprocess.run([
        "docker", "build",
        "-f", "Dockerfile.build",
        "-t", f"wheel-builder-{package_name}",
        "."
    ], check=True)
    
    # Run the container to build the wheel
    os.makedirs("dist", exist_ok=True)
    subprocess.run([
        "docker", "run",
        "--rm",
        "-v", f"{os.getcwd()}/dist:/output",
        f"wheel-builder-{package_name}"
    ], check=True)
    
    # Clean up
    os.remove("Dockerfile.build")
    print(f"✓ Built {package_name}=={version}")

def main():
    # Load packages from toml
    with open("packages.toml", "r") as f:
        config = toml.load(f)
    
    packages = config.get("package", [])
    
    if not packages:
        print("No packages found in packages.toml")
        return
    
    print(f"Building {len(packages)} packages for armv7l...")
    
    for pkg in packages:
        name = pkg["name"]
        version = pkg["version"]
        
        try:
            build_wheel_in_docker(name, version)
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build {name}=={version}: {e}")
            continue
    
    print("\nBuild complete! Wheels saved in dist/")

if __name__ == "__main__":
    main()
