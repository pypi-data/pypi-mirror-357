from setuptools import setup, find_packages

setup(
    name='taskflow_work',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Seu Nome',
    description='Uma library simples de orquestração de tarefas estilo Airflow.',
    python_requires='>=3.7',
)