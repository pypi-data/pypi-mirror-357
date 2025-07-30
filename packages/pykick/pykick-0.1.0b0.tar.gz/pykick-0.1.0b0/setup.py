import os # Used to obtain Git version information. See calculate_version function.

from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

def generate_meta():
    """
    Generates the meta information for the package.
    This function reads the meta information from the meta module and returns it.
    """
    return {
        "version": calculate_version(),
        "author": "Pavalso",
        "license": "MIT",
        "description": "A Python library for interacting with the Kick streaming platform API.",
        "package_name": "pykick",
    }

def calculate_version():
    """
    Calculates the version of the package using Git.
    This function checks if the Git repository is currently tagged.
    If a tag is found, it returns the tag as the version.
    If no tags are found, returns current commit hash + version.
    If no repository is found, returns 
    """
    current_tag = os.popen("git describe --exact-match --tags").read().strip()
    closest_tag = os.popen("git describe --tags --abbrev=0").read().strip()
    commit_hash = os.popen("git rev-parse --short HEAD").read().strip()
    commit_count = os.popen("git rev-list --all --count").read().strip()
    
    with open("kickpy/meta.py") as f:
        version_line = [line for line in f if line.startswith("__version__")][0]
        __version__ = version_line.split('=')[1].strip().strip('"')
    
    version = f"{__version__}+{commit_hash}.{commit_count}"
        
    if not current_tag  and not closest_tag and not commit_hash:
        # If no Git information is available, fallback to the default version.
        return __version__

    elif current_tag:
        # If the current commit is tagged, return the tag as the version.
        version = current_tag

    elif closest_tag:
        # If no exact tag, returns the closest tag + commit hash.
        version = f"{closest_tag}+{commit_hash}.{commit_count}"

    # If no tags are found, return the commit hash + commit count.
    return version

meta = generate_meta()

setup(
    name=meta["package_name"],
    version=meta["version"],
    author=meta["author"],
    description=meta["description"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pavalso/kick.py",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    license=meta["license"],
    keywords="kick streaming python api library",
    project_urls={
        "Documentation": "https://kickpy.readthedocs.io",
        "Source": "https://github.com/pavalso/kick.py",
    }
)
