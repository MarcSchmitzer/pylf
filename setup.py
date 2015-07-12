import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
requires = [
    "Babel>=1.3",
    "Jinja2>=2.7",
    "PyICU>=1.9",
    "pyramid>=1.5",
    "pyramid-jinja2>=2.5",
    "simplepam>=0.1",
    "WebOb>=1.4",
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
)
