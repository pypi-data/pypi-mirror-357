from setuptools import setup, find_packages

#Leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
     name="santis1986-hack4you",
     version="0.1.0",
     packages=find_packages(),
     install_requires=[],
     author="Marcelo Vazquez",
     description="Una biblioteca para consultar cursos de hack4you.",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://hack4u.io",
)
