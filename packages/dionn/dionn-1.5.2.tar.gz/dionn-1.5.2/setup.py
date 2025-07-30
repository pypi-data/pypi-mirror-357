import setuptools
from pathlib import Path

# Lee el README para la descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dionn",
    version="1.5.2",  # Aumenta versión en cada publicación
    author="Juan Zamora, Sebastian Vegas, Kerlyns Martínez, Daira Velandia, Sebastián Jara, Pascal Sigel",
    author_email="",
    description="Detection Intra-class Outliers with Neural Networks (DIONN) algorithm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juanzamorai/intracluster-filtering",
    license="MIT",
    packages=["dionn", "utils"],
    install_requires=[
        "numpy==1.25.2",
        "scikit-learn",
        "tensorflow==2.10.0",
        "keras==2.10.0",
        "protobuf>=3.9.2,<3.20",
        "gast",
        "astunparse",
        "flatbuffers>=23.5.26",
        "google-pasta>=0.1.1",
        "libclang>=13.0.0",
        "opt-einsum>=2.3.2",
        "plotly",
        "ml-dtypes==0.3.1",
        "seaborn",
        "scipy==1.14.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10.14",
)
