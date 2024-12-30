"""Version information."""
import re
from pathlib import Path


def get_version() -> str:
    """Get version from pyproject.toml."""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            version_match = re.search(r'version\s*=\s*"(.*?)"', content)
            if version_match:
                return version_match.group(1)
    except Exception:
        pass

    # Fallback for installed package
    try:
        from importlib.metadata import version
        return version("scarf-sdk")
    except Exception:
        return "unknown"

__version__ = get_version()
