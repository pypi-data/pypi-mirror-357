from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='cursofiap-package-acrossi',
    version='1.0.0',
    packages=find_packages(),
    description='Descricao da sua lib cursoFiap',
    author='Angelo Rossi',
    author_email='yrc_legna@hotmail.com',
    url='https://github.com/AngeloCRossi/MLET_PYTHON_ML_IA_AULA2/tree/744ea9db06fe2ff4b011a092dc9e0c022ca4bdd0/AULA3',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown'
)
