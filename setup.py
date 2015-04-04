from setuptools import setup, find_packages

setup(
  name = 'recast-hype-demo',
  version = '0.0.1',
  description = 'recast-hype-demo',
  url = 'http://github.com/recast-hep/recast-hype-demo',
  author = 'Lukas Heinrich',
  author_email = 'lukas.heinrich@cern.ch',
  packages = find_packages(),
  include_package_data = True,
  install_requires = [
    'Flask',
    'yoda',
    'pyyaml'
  ],
  dependency_links = [
  ]
)
