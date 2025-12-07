#!/usr/bin/env python3
"""Generate a PEP 503 compliant package index from built wheels"""

from pathlib import Path
from html import escape
import re

def normalize_package_name(name):
    """Normalize package name per PEP 503"""
    return re.sub(r"[-_.]+", "-", name).lower()

def generate_index():
    """Generate index.html and per-package pages"""
    
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Find all wheel files
    wheels = list(dist_dir.glob("*.whl"))
    
    if not wheels:
        print("No wheels found in dist/")
        return
    
    # Group wheels by package name
    packages = {}
    for wheel in wheels:
        # Extract package name from wheel filename
        # Format: {distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl
        parts = wheel.name.split("-")
        if len(parts) >= 3:
            pkg_name = normalize_package_name(parts[0])
            if pkg_name not in packages:
                packages[pkg_name] = []
            packages[pkg_name].append(wheel)
    
    # Generate main index
    main_index = """<!DOCTYPE html>
<html>
<head>
    <title>Simple Package Index</title>
    <meta name="api-version" value="2" />
</head>
<body>
    <h1>Simple Package Index</h1>
"""
    
    for pkg_name in sorted(packages.keys()):
        main_index += f'    <a href="{pkg_name}/">{escape(pkg_name)}</a><br/>\n'
    
    main_index += """</body>
</html>
"""
    
    (dist_dir / "index.html").write_text(main_index)
    print(f"✓ Generated main index with {len(packages)} packages")
    
    # Generate per-package pages
    for pkg_name, wheels in packages.items():
        pkg_dir = dist_dir / pkg_name
        pkg_dir.mkdir(exist_ok=True)
        
        pkg_index = f"""<!DOCTYPE html>
<html>
<head>
    <title>Links for {escape(pkg_name)}</title>
    <meta name="api-version" value="2" />
</head>
<body>
    <h1>Links for {escape(pkg_name)}</h1>
"""
        
        for wheel in wheels:
            wheel_name = wheel.name
            # Link is relative to package directory
            pkg_index += f'    <a href="../{escape(wheel_name)}">{escape(wheel_name)}</a><br/>\n'
        
        pkg_index += """</body>
</html>
"""
        
        (pkg_dir / "index.html").write_text(pkg_index)
        print(f"✓ Generated index for {pkg_name} ({len(wheels)} wheels)")
    
    print("\n✓ Index generation complete!")

if __name__ == "__main__":
    generate_index()
