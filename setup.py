import os

from setuptools import setup

# Set external files
try:
    from pypandoc import convert

    README = convert('README.md', 'rst')
except ImportError:
    README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()

setup(
    name='django-zappa',
    version='0.13.1',
    packages=['django_zappa'],
    install_requires=required,
    include_package_data=True,
    license='MIT License',
    description='Serverless Django With AWS Lambda + API Gateway',
    long_description=README,
    url='https://github.com/Miserlou/django-zappa',
    download_url='https://github.com/Miserlou/django-zappa',
    author='Rich Jones',
    author_email='rich@openwatch.net',
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
