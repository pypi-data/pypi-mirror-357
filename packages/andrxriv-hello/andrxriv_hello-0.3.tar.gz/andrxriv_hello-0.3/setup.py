from setuptools import setup, find_packages

setup(
    name='andrxriv_hello',
    version='0.3',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "andrxriv-hello = andrxriv_hello:hello",
        ],
    },
)