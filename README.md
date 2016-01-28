![Logo placeholder](http://i.imgur.com/vLflpND.gif)
# django-zappa [![Build Status](https://travis-ci.org/Miserlou/django-zappa.svg)](https://travis-ci.org/Miserlou/django-zappa)
#### Serverless Django with AWS Lambda + API Gateway

**django-zappa** makes it super easy to deploy Django applications on AWS Lambda + API Gateway. Think of it as "serverless" web hosting for your Django apps. [See in action here!](https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/prod)

That means:

* **No more** tedious web server configuration!
* **No more** paying for 24/7 server uptime!
* **No more** worrying about load balancing / scalability!
* **No more** worrying about keeping servers online!
* **No more** worrying about security vulernabilities and patches!

**django-zappa** handles:

* Packaging projects into Lambda-ready zip files and uploading them to S3
* Correctly setting up IAM roles and permissions
* Automatically configuring API Gateway routes, methods and integration responses
* Deploying the API to various stages of readiness

__Awesome!__

This project is for Django-specific integration. If you are intersted in how this works under the hood, you should look at the **[Zappa core library](https://github.com/Miserlou/Zappa)**, which can be used by any WSGI-compatible web framework.

## Installation

    $ pip install django-zappa

## Configuration

There are a few settings that you must define before you deploy your application. First, you must have your AWS credentials stored in _~/.aws/credentials'_.

Finally, define a ZAPPA_SETTINGS setting in your local settings file which maps your named deployment environments to deployed settings and an S3 bucket (which must already be created). These can be named anything you like, but you may wish to have seperate _dev_, _staging_ and _production_ environments in order to separate your data.

```python
ZAPPA_SETTINGS = {
    'production': {
       's3_bucket': 'production-bucket',
       'settings_file': '~/Projects/MyApp/settings/production_settings.py',
    },
    'staging': {
       's3_bucket': 'staging-bucket',
       'settings_file': '~/Projects/MyApp/settings/staging_settings.py',
    },
}
```

Notice that each environment defines a path to a settings file. This file will be used as your _server-side_ settings file. Specifically, you will want to define [a new SECRET_KEY](https://gist.github.com/Miserlou/a9cbe22d06cbabc07f21), as well as your deployment DATABASES information. 

## Basic Usage

#### Initial Deployments

Once your settings are configured, you can package and deploy your Django application to an environment called 'production' with a single command:

    $ python manage.py deploy production
    Deploying..
    Your application is now live at: https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/production

#### Updates

If your application has already been deployed and you only need to upload new Python code, but not touch the underlying routes, you can simply:

    $ python manage.py update production
    Updating..
    Your application is now live at: https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/production

#### Management

If you want to invoke Django management commands on the remote Zappa instance, you simply call the 'invoke' management command locally:

    $ python manage.py invoke production check
    System check identified no issues (0 silenced).

## TODO

This project is very young, so there is still plenty to be done. Contributions are more than welcome! Please file tickets before submitting patches, and submit your patches to the 'dev' branch.

Things that need work right now:

* ORM/DB support
* Testing
* Route53 Integration
* SSL Integration
* Package size/speed optimization
* Fix the "hot-start" problem
* Feedback
* A nifty logo
* Real documentation / website!