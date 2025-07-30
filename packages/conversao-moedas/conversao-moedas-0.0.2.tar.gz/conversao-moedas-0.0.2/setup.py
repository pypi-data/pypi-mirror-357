from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup (
    name="conversao-moedas",
    version="0.0.2",
    author="Guilherme Kenzo Watanabe Fujimura",
    author_email="gkwfuji@gmail.com",
    description="Conversor de moedas",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/K3nz002/criacao_pacotes",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)