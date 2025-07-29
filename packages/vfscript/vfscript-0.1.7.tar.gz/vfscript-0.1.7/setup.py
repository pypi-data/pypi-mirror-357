# setup.py
import io, os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vfscript",
    version="0.1.7",
    author="SantiBS",
    author_email="santiagobergamin@gmail.com",
    description="Vacancy Finder Script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TiagoBe0/VFScript-CDScanner",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",

    package_dir={"": "src"},
    packages=find_packages(where="src"),

    include_package_data=True,
    package_data={
        "vfscript": ["*.json", "resources/*.yaml"],
    },

    install_requires=[
        "numpy",
        "pandas",
        "ovito",
        "xgboost",
        "scikit-learn",
    ],

    entry_points={
        "console_scripts": [
            "vfscript = vfscript.__main__:main",
        ],
    },
)
