from setuptools import setup, find_packages

setup(
    name='HostLocal',
    version='1.0.0',
    description='A simple Flask-based file explorer with batch upload and preview support',
    author='Your Name',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
    ],
    entry_points={
        'console_scripts': [
            'host=pyfileexplorer.app:main',
        ],
    },
)
