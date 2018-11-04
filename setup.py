import os
from setuptools import setup, find_packages

DEPENDENCIES = [
    'click',
    'colorama==0.3.9',
    'halo',
    'PyYAML',
    'PTable',
    'pylint',
    'kubernetes'

]

setup(
    name='kubeasy',
    version='0.1.0',
    py_modules=['kubeasy'],
    python_requires='>=3',
    packages = find_packages(exclude=["*.tests", "tests"]),
    author='Cizer Pereira',
    author_email='cizer.ciz@gmail.com',
    url='https://github.com/C123R/kubeasy',
    include_package_data=True,
    install_requires=DEPENDENCIES,
    entry_points='''
        [console_scripts]
        kubeasy=kubeasy:cli
    ''',
)
