#!/usr/bin/env python3
"""Build wheels for packages listed in packages.toml"""

import toml
import subprocess
import os
from pathlib import Path

def build_wheel_in_docker(package_name, version, python_version):
    """Build a wheel using Docker with ARM emulation"""
    
    # Check if wheel already exists
    wheel_pattern = f"{package_name.replace('-', '_')}-{version}-*-cp{python_version.replace('.', '')}-*"
    existing_wheels = list(Path("dist").glob(wheel_pattern))
    
    if existing_wheels:
        print(f"⏭️  Skipping {package_name}=={version} (py{python_version}) - wheel already exists")
        return True
    
    # Create a temporary Dockerfile
    dockerfile_content = f"""
FROM python:{python_version}-slim

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
    
    # Build the Docker image for ARM platform
    print(f"Building {package_name}=={version} (py{python_version})...")
    subprocess.run([
        "docker", "buildx", "build",
        "--platform", "linux/arm/v7",
        "-f", "Dockerfile.build",
        "-t", f"wheel-builder-{package_name}-py{python_version}",
        "--load",
        "."
    ], check=True)
    
    # Run the container to build the wheel
    os.makedirs("dist", exist_ok=True)
    subprocess.run([
        "docker", "run",
        "--platform", "linux/arm/v7",
        "--rm",
        "-v", f"{os.getcwd()}/dist:/output",
        f"wheel-builder-{package_name}-py{python_version}"
    ], check=True)
    
    # Clean up
    os.remove("Dockerfile.build")
    print(f"✓ Built {package_name}=={version} (py{python_version})")
    return True

def main():
    # Load packages from toml
    with open("packages.toml", "r") as f:
        config = toml.load(f)
    
    packages = config.get("package", [])
    python_versions = config.get("python_versions", ["3.11", "3.12"])
    
    if not packages:
        print("No packages found in packages.toml")
        return
    
    print(f"Building {len(packages)} packages for armv7l (Python: {', '.join(python_versions)})...")
    
    for pkg in packages:
        name = pkg["name"]
        version = pkg["version"]
        
        for py_ver in python_versions:
            try:
                build_wheel_in_docker(name, version, py_ver)
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to build {name}=={version} (py{py_ver}): {e}")
                continue
    
    print("\nBuild complete! Wheels saved in dist/")

if __name__ == "__main__":
    main()
