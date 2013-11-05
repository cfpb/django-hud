import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django_hud',
    version=__import__('hud_api_replace').__version__,
    author='CFPB',
    author_email='tech@cfpb.gov',
    packages=['hud_api_replace'],
    include_package_data=True,
    description=u'An API to return a Counseling Agencies list',
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=read_file('README.md'),
    zip_safe=False,
)
