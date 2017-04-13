import os
from setuptools import setup, find_packages


def long_desc(root_path):
    FILES = ['README.rst']
    for filename in FILES:
        filepath = os.path.realpath(os.path.join(root_path, filename))
        if os.path.isfile(filepath):
            with open(filepath, mode='r') as f:
                yield f.read()


HERE = os.path.abspath(os.path.dirname(__file__))
long_description = "\n\n".join(long_desc(HERE))


def get_version(root_path):
    with open(os.path.join(root_path, 'lbutils', '__init__.py')) as f:
        for line in f:
            if line.startswith('__version__ ='):
                return line.split('=')[1].strip().strip('"\'')

setup(
    name='django-lbutils',
    version=get_version(HERE),
    description='A set of useful function/tags/filter for Django',
    long_description=long_description,
    author='vicalloy',
    author_email='zbirder@gmail.com',
    url='https://github.com/vicalloy/lbutils',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Django>=1.6.0'],
    extras_require={
        'django-crispy-forms': [
            'django-crispy-forms>1.4',
        ],
        'xlsxwriter': [
            'xlsxwriter>0.8',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
    ],
    zip_safe=False,
    tests_require=["Django>=1.6.0"],
    test_suite='runtests.runtests',
    package_data={
        'lbutils': [
            'locale/*/LC_MESSAGES/django.po', 'locale/*/LC_MESSAGES/django.mo'
        ],
    },
)
