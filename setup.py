from setuptools import find_packages
from setuptools import setup

from pip.req import parse_requirements


def _get_requirements():
    install_reqs = parse_requirements('requirements.txt')
    requirements = [str(ir.req) for ir in install_reqs]
    return requirements


setup(
    name='Pendium',
    version='1.0',
    packages=find_packages(),
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=_get_requirements(),
    include_package_data=True,
    author='Gil Goncalves',
    author_email='lursty@gmail.com',
    url='https://github.com/lurst/txt2bootstrap',
    entry_points="""
[console_scripts]
pendium = pendium:run
""",
)
