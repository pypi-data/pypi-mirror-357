# setup.py
import io, os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="VFScript",
    version="0.1.1",
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

    # <- clave para proyectos multi-paquete
    package_dir={"": "src"},
    packages=find_packages(where="src"),  

    # incluye archivos listados en MANIFEST.in o package_data
    include_package_data=True,
    package_data={
        # empaca todos los .yaml dentro de resources/
        "miflpaquete": ["resources/*.yaml"],
    },

    install_requires=[
        "numpy",
        "pandas",
        "ovito",
        "xgboost",
        "scikit-learn"
        # etc…
    ],

    entry_points={
        "console_scripts": [
            "miflp = miflpaquete.core:main",
        ],
    },
)
