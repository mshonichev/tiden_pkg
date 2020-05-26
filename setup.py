from setuptools import find_packages, setup
import re
import sys
from os.path import join, dirname, isfile, exists
from os import listdir

version = ''
with open(join('src', 'tiden', '__version__.py'), 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

if not exists('requirements.txt'):
    raise RuntimeError('Cannot find version information')

with open('requirements.txt', 'r') as fd:
    requirements = [req.strip() for req in fd.readlines() if not req.strip().startswith('#')]

scripts = [join('bin', script) for script in listdir(join(dirname(__file__), 'bin')) if
           isfile(join(dirname(__file__), 'bin', script)) and script.endswith('.py')]

setup(
    version=version,
    platforms=["any"],
    keywords="testing ignite",
    license="apache2.0",
    url="http://github.com/gridgain/tiden",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    scripts=scripts,
    python_requires='>=3.7, <4',
    install_requires=requirements,
)
