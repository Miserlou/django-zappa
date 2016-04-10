<p align="center">
  <img src="http://i.imgur.com/oePnHJn.jpg" alt="Zappa Rocks!"/>
</p>

## django-zappa - Serverless Django

[![Django-CC](https://img.shields.io/badge/Django-CC-ee66dd.svg)](https://github.com/codingjoe/django-cc) 
[![Build Status](https://travis-ci.org/Miserlou/django-zappa.svg)](https://travis-ci.org/Miserlou/django-zappa) 
[![Coverage](https://img.shields.io/coveralls/Miserlou/django-zappa.svg)](https://coveralls.io/github/Miserlou/django-zappa) 
[![Slack](https://img.shields.io/badge/chat-slack-ff69b4.svg)](https://slackautoinviter.herokuapp.com/)

**django-zappa** makes it super easy to deploy Django applications on AWS Lambda + API Gateway. Think of it as "serverless" web hosting for your Django apps.

That means:

* **No more** tedious web server configuration!
* **No more** paying for 24/7 server uptime!
* **No more** worrying about load balancing / scalability!
* **No more** worrying about keeping servers online!
* **No more** worrying about security vulnerabilities and patches!

**django-zappa** handles:

* Packaging projects into Lambda-ready zip files and uploading them to S3
* Correctly setting up IAM roles and permissions
* Automatically configuring API Gateway routes, methods and integration responses
* Turning API Gateway requests into valid WSGI, and returning API Gateway compatible HTTP responses
* Deploying your application to various stages of readiness (dev, staging, prod)

__Awesome!__

[See it in action here!](https://zappa.gun.io/) You can also watch a **[screencast on how to use django-zappa](https://www.youtube.com/watch?v=plUrbPN0xc8&feature=youtu.be)**.

This project is for Django-specific integration. If you are interested in how this works under the hood, you should look at the **[Zappa core library](https://github.com/Miserlou/Zappa)**, which can be used by any WSGI-compatible web framework.

## Installation

_Before you begin, make sure you have a valid AWS account and your [AWS credentials file](https://blogs.aws.amazon.com/security/post/Tx3D6U6WSFGOK2H/A-New-and-Standardized-Way-to-Manage-Credentials-in-the-AWS-SDKs) is properly installed._

**django-zappa** can easily be installed through pip, like so:

    $ pip install django-zappa

In your Django settings, you will need to add `django_zappa` to your installed apps in order to add Zappa commands to your management script.

```python
INSTALLED_APPS = [
    ...
    'django_zappa',
]
```

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

Notice that each environment defines a path to a settings file. This file will be used as your _server-side_ settings file. Specifically, you will want to define [a new SECRET_KEY](https://gist.github.com/Miserlou/a9cbe22d06cbabc07f21), as well as your deployment DATABASES information. Zappa now supports both _MySQL-Python_ and _pyscopg2_ via [lambda-packages](https://github.com/Miserlou/lambda-packages).

## Basic Usage

#### Initial Deployments

Once your settings are configured, you can package and deploy your Django application to an environment called 'production' with a single command:

    $ python manage.py deploy production
    Deploying..
    Your application is now live at: https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/production

And now your app is **live!** How cool is that?!

#### Updates

If your application has already been deployed and you only need to upload new Python code, but not touch the underlying routes, you can simply:

    $ python manage.py update production
    Updating..
    Your application is now live at: https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/production

#### Rollback

You can also rollback the deployed code to a previous version by supplying the number of revisions to return to. For instance, to rollback to the version deployed 3 versions ago:

    $ python manage.py rollback production 3

#### Management

If you want to invoke Django management commands on the remote Zappa instance, you simply call the 'invoke' management command locally:

    $ python manage.py invoke production check
    System check identified no issues (0 silenced).

#### Tailing Logs

You can watch the logs of a deployment by calling the 'tail' management command.

    $ python manage.py tail production

## Advanced Usage

There are other settings that you can define in your ZAPPA_SETTINGS
to change Zappa's behavior. Use these at your own risk!

```python
ZAPPA_SETTINGS = {
    'dev': {
        'aws_region': 'us-east-1', # AWS Region (default US East),
        'domain': 'yourapp.yourdomain.com', # Required if you're using a domain
        'http_methods': ['GET', 'POST'], # HTTP Methods to route,
        'integration_response_codes': [200, 301, 404, 500], # Integration response status codes to route
        'memory_size': 512, # Lambda function memory in MB
        'method_response_codes': [200, 301, 404, 500], # Method response status codes to route
        'parameter_depth': 10, # Size of URL depth to route. Defaults to 5.
        'role_name': "MyLambdaRole", # Lambda execution Role
        's3_bucket': 'dev-bucket', # Zappa zip bucket,
        'settings_file': '~/Projects/MyApp/settings/dev_settings.py', # Server side settings file location,
        'touch': False, # GET the production URL upon initial deployment (default True)
        'use_precompiled_packages': True, # If possible, use C-extension packages which have been pre-compiled for AWS Lambda
        'vpc_config': { # Optional VPC configuration for Lambda function
            'SubnetIds': [ 'subnet-12345678' ], # Note: not all availability zones support Lambda!
            'SecurityGroupIds': [ 'sg-12345678' ]
        }
    }
}
```

#### Keeping the server warm

Lambda has a limitation that functions which aren't called very often take longer to start - sometimes up to ten seconds. However, functions that are called regularly are cached and start quickly, usually in less than 50ms. To ensure that your servers are kept in a cached state, you can [manually configure](http://stackoverflow.com/a/27382253) a scheduled task for your Zappa function that'll keep the server cached by calling it every 5 minutes. There is currently no way to configure this through API, so you'll have to set this up manually. When this ability is available via API, django-zappa will configure this automatically. It would be nice to also add support LetsEncrypt through this same mechanism.

#### Enabling CORS

To enable Cross-Origin Resource Sharing (CORS) for your application, follow the [AWS 'How to CORS' Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html) to enable CORS via the API Gateway Console. Don't forget to re-deploy your API after making the changes!

## TODO

This project is very young, so there is still plenty to be done. Contributions are more than welcome! Please file tickets before submitting patches, and submit your patches to the 'dev' branch.

Things that need work right now:

* Testing!
* Feedback!
* Real documentation / website!

## [Contributing](CONTRIBUTING.md)

## [License](LICENSE)
