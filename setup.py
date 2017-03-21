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


setup_requires = [
    'setuptools-git-version==1.0.3',
]


install_requires = [
    'address==0.1.1',
    'Django>=1.8,<1.11',
    'geocoder==1.12.0',
]


testing_extras = [
    'coverage>=3.7.0',
    'mock>=1.0.0',
]


setup(
    name='django_hud',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    maintainer='CFPB',
    maintainer_email='tech@cfpb.gov',
    packages=find_packages(),
    include_package_data=True,
    description='An API to return Counseling Agencies list',
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=read_file('README.md'),
    zip_safe=False,
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
    },
)
