from setuptools import setup, find_packages

setup(
  name = 'recast-hype-demo',
  version = '0.0.1',
  description = 'recast-hype-demo',
  url = 'http://github.com/lukasheinrich/recast-hype-demo',
  author = 'Lukas Heinrich',
  author_email = 'lukas.heinrich@cern.ch',
  packages = find_packages(),
  include_package_data = True,
  install_requires = [
    'Flask',
    'celery',
    'requests',
    'recast-api',
    'yoda',
    'socket.io-python-emitter',
    'redis'
  ],
  dependency_links = [
    'https://github.com/ziyasal/socket.io-python-emitter/tarball/master#egg=socket.io-python-emitter-0.1.3',
    'https://github.com/cranmer/recast-api/tarball/master#egg=recast-api-0.0.1'
  ]
)
