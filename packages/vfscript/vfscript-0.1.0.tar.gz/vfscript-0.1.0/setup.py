# setup.py
import io
import os
from setuptools import setup, find_packages

# Lee el long_description desde el README.md
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vfscript",
    version="0.1.0",
    author="Santiago Bergamin",
    author_email="santiagobergamin@gmail.com",
    description="Vacancy Calculator Script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TiagoBe0/VFScript-CDScanner",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],

    # Descubre los paquetes bajo src/ automáticamente
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    # Incluye archivos .json que estén junto al código
    include_package_data=True,
    package_data={
        "vfsdoc": ["*.json"],
    },

    install_requires=[
        "numpy",
        "pandas",
        "ovito",
        "xgboost",
        "scikit-learn"
    ],

    # Si quieres exponer un script ejecutable, por ejemplo "vfsdoc"
    entry_points={
        "console_scripts": [
            "vfsdoc = vfsdoc.main:main",
        ],
    },
)
