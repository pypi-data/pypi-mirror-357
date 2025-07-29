from setuptools import setup, find_packages

setup(
    name='ProjetoUmMADS',
    version='0.1.1',
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
