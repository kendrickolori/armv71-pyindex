# ARM Wheel Index

Pre-built Python wheels for armv7l architecture. No more waiting for slow builds!

## Quick Setup

### Enable GitHub Pages

1. Go to repository settings
2. Navigate to "Pages" section
3. Source: Deploy from a branch
4. Branch: `gh-pages` / `root`
5. Save

### Use Your Index

On your ARM device:

```bash
# Install from your index
pip install rpds-py \
  --extra-index-url https://kendrickolori.github.io/armv71-pyindex/

# Or with uv
uv pip install rpds-py \
  --extra-index-url https://kendrickolori.github.io/armv71-pyindex/
```

**Add to pyproject.toml:**

```toml
[tool.uv]
extra-index-url = ["https://kendrickolori.github.io/armv71-pyindex/"]
```

## Adding New Packages

Edit `packages.toml` and push:

```toml
[[package]]
name = "cryptography"
version = "41.0.7"
```

The workflow will build it automatically within ~10-15 minutes.

## How It Works

1. GitHub Actions uses QEMU to emulate ARM architecture
2. Builds wheels inside `arm32v7/python` Docker containers
3. Generates a PEP 503 compliant package index
4. Deploys to GitHub Pages
5. Your ARM device downloads pre-built wheels instead of building from source
