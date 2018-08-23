import os
from setuptools import setup

setup(
    name='kubeasy',
    version='0.1',
    py_modules=['kubeasy'],
    install_requires=[
        'Click',
        'logging-utils',
    ],
    entry_points='''
        [console_scripts]
        kubeasy=kubeasy:cli
    ''',
)
