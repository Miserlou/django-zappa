from distutils.core import setup

setup(
  name = 'django-zappa',
  packages = ['django-zappa'], 
  version = '0.0.1',
  description = 'Django on AWS Lambda',
  license='MIT License',
  author='Rich Jones',
  author_email='rich@openwatch.net',
  url='https://github.com/Miserlou/django-zappa',
  keywords = ['django', 'aws', 'lambda', 'apigateway'], # arbitrary keywords
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
