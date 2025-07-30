import sys
from setuptools import setup

args = ' '.join(sys.argv).strip()
if not any(args.endswith(suffix) for suffix in ['setup.py check -r -s', 'setup.py sdist']):
    raise ImportError('This package is temporarily parked to protect against typosquating. Coming soon.')

setup(
    classifiers=['Development Status :: 7 - Inactive'],
    description='This package is temporarily parked to protect against typosquating. Coming soon.',
    long_description='This package is temporarily parked to protect against typosquating. Coming soon.',
    name='aws-app-framework-for-github-apps-on-aws-client',
    version='0.0.1a1'
)
