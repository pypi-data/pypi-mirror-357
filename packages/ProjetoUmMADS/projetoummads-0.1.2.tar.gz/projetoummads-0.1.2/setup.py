from setuptools import setup, find_packages
from os import path

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ProjetoUmMADS',
    version='0.1.2',
    author='JoaoPinheiro1311',
    author_email='a040698@ipmaia.pt',
    description='Projeto de MADS - Grupo 7 - Gestão de Stocks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/JoaoPinheiro1311/ProjetoUmMADS',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
