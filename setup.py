import os
from setuptools import setup, find_packages

setup(
    name='kubeasy',
    version='0.1',
    py_modules=['kubeasy'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        kubeasy=kubeasy:cli
    ''',
)
