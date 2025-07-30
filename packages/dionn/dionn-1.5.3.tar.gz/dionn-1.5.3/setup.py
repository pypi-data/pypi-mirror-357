import setuptools
from pathlib import Path

# Lee el README para la descripción larga
long_description = Path("README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="dionn",
    version="1.5.3",  # Sube versión
    author="Juan Zamora, Sebastian Vegas, Kerlyns Martínez, Daira Velandia, Sebastián Jara, Pascal Sigel",
    author_email="",
    description="Detection Intra-class Outliers with Neural Networks (DIONN) algorithm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juanzamorai/intracluster-filtering",
    license="MIT",
    packages=["dionn", "utils"],
    python_requires=">=3.10.14",
    install_requires=[
        "numpy>=1.24,<2.0",             # así Pip podrá instalar numpy 1.24.x si 1.25.x no tiene rueda
        "scikit-learn>=1.0,<2.0",
        "tensorflow>=2.10.0,<3.0",      # acepta tf>=2.10 hasta antes de 3.x; pip elegirá la última wheel
        "keras>=2.10.0,<3.0",
        "protobuf>=3.9.2,<3.20",
        "gast>=0.4.0",
        "astunparse>=1.6.3",
        "flatbuffers>=23.5.26",
        "google-pasta>=0.1.1",
        "libclang>=13.0.0",
        "opt-einsum>=2.3.2",
        "plotly>=5.0.0",
        "ml-dtypes>=0.3.1,<0.4",
        "seaborn>=0.12.0",
        "scipy>=1.10,<2.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
