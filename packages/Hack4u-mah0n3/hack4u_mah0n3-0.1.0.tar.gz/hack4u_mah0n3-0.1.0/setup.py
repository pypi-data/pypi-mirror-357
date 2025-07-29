from setuptools import setup, find_packages

# Leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Hack4u_mah0n3",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Marcelo Vázquez",
    description="Una biblioteca para consultar cursos de Hack4U",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Cambia si usas otra licencia
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
