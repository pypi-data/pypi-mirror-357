from setuptools import setup, find_packages
from pathlib import Path

# Long description from README
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="cipherdropx",
    version="1.0.0",
    description="Resilient YouTube signature deciphering engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Klypse",
    url="https://github.com/Klypse/CipherDropx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    zip_safe=False,
)