from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup (
    name="conversao-moedas",
    version="0.0.1",
    author="Guilherme Kenzo Watanabe Fujimura",
    author_email="gkwfuji@gmail.com",
    description="Conversor de moedas",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url='https://github.com/GuilhermeKenzo/conversao-moedas-package',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)