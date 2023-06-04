from setuptools import setup, Extension
import subprocess
import os

def get_git_revision_short_hash() -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "DEV_BRANCH_UNDEFINED"

VERSION = os.environ.get("ANCYR_TOOLS_RELEASE_VERSION", f"{get_git_revision_short_hash()}")

def main():
    setup(
        name="ancyr-tools",
        version=VERSION,
        description="Python tools for Ancyr development",
        author="Adam Schafer",
        author_email="adam.schafer@bgnetworks.com",
    )

if __name__ == "__main__":
    main()