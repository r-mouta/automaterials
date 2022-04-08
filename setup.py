from setuptools import find_packages, setup


def read(filename):
    return [requires.strip() for requires in open(filename).readlines()]


setup(
    name='automaterials',
    version='0.1.0',
    description='automaterials',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read('requirements.txt'),
    extras_require={'dev': read('requirements-dev.txt')},
)
