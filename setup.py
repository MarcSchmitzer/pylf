import os

from babel.messages import frontend as babel
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid>=1.0.2',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'waitress'
]

setup(name='pylf',
      version='0.0',
      description='File Manager Web-App',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Marc Schmitzer',
      author_email='marc@marc-schmitzer.de',
      url='https://www.marc-schmitzer.de',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pylf",
      entry_points="""\
      [paste.app_factory]
      main = pylf:main
      """,
      cmdclass = {
          'compile_catalog': babel.compile_catalog,
          'extract_messages': babel.extract_messages,
          'init_catalog': babel.init_catalog,
          'update_catalog': babel.update_catalog,
      },
)
