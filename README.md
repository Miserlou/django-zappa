![Logo](http://i.imgur.com/vLflpND.gif)
# django-zappa [![Build Status](https://travis-ci.org/Miserlou/django-zappa.svg)](https://travis-ci.org/Miserlou/django-zappa) [![Slack](https://img.shields.io/badge/chat-slack-ff69b4.svg)](https://slackautoinviter.herokuapp.com/)
#### Serverless Django with AWS Lambda + API Gateway

**django-zappa** makes it super easy to deploy Django applications on AWS Lambda + API Gateway. Think of it as "serverless" web hosting for your Django apps. 

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
* Turning API Gateway requests into valid WSGI, and returning API Gateway compatible HTTP responses 
* Deploying your to various stages of readiness (dev, staging, prod)

__Awesome!__

[See it in action here!](https://zappa.gun.io/) You can also watch a **[screencast on how to use django-zappa](https://www.youtube.com/watch?v=plUrbPN0xc8&feature=youtu.be)**.

This project is for Django-specific integration. If you are intersted in how this works under the hood, you should look at the **[Zappa core library](https://github.com/Miserlou/Zappa)**, which can be used by any WSGI-compatible web framework.

## Installation

    $ pip install django-zappa

## Configuration

There are a few settings that you must define before you deploy your application. First, you must have your AWS credentials stored in _~/.aws/credentials_ (you may have to create this file). This is in ConfigParser format and must include at least `aws_access_key_id` and `aws_secret_access_key` within a 'default' section, ex:

```
[default]
aws_access_key_id=XXXXXXXXXXXXXXXXXXXX
aws_secret_access_key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
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

Notice that each environment defines a path to a settings file. This file will be used as your _server-side_ settings file. Specifically, you will want to define [a new SECRET_KEY](https://gist.github.com/Miserlou/a9cbe22d06cbabc07f21), as well as your deployment DATABASES information. 

#### A Note About Databases

Since Zappa requirements are called from a bundled version of your local environment and not from pip, and because we have no way to determine what platform our Zappa handler will be executing on, we need to make sure that we only use portable packages. So, instead of using the default MySQL engine, we will instead need to use _mysql-python-connector_. 

That means your app's settings file will need an entry that looks like something this (notice the Engine field):

```python
DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'your_db_name',
        'USER': 'your_db_username',
        'PASSWORD': 'your_db_password',
        'HOST': 'your_db_name.your_db_id.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}
```

At time of writing, there seems to be a problem with the Python MySQL connector when calling the initial 'migrate'. You can remedy this by using the usual 'django.db.backends.mysql' for your initial migration from your local machine and just using 'mysql.connector.django' in your remote settings.

Currently, Zappa only supports MySQL and Aurora on RDS.

#### Middleware

Zappa requires special middleware for handling cookies, so in your remote settings file, you must include _ZappaMiddleware_ as the first item in your *MIDDLEWARE_CLASSES*:

```python
MIDDLEWARE_CLASSES = (
    'django_zappa.middleware.ZappaMiddleware',
    ...
)
```

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
        'method_response_codes': [200, 301, 404, 500], # Method response status codes to route
        'parameter_depth': 10, # Size of URL depth to route. Defaults to 5.
        'role_name': "MyLambdaRole", # Lambda execution Role
        's3_bucket': 'dev-bucket', # Zappa zip bucket,
        'settings_file': '~/Projects/MyApp/settings/dev_settings.py', # Server side settings file location,
        'touch': False, # GET the production URL upon initial deployment (default True)
        'memory_size': 512, # Lambda function memory in MB
        'vpc_config': { # Optional VPC configuration for Lambda function
            'SubnetIds': [ 'subnet-12345678' ], # Note: not all availability zones support Lambda!
            'SecurityGroupIds': [ 'sg-12345678' ]
        }
    }
}
```

### Let's Encrypt SSL

Zappa has very basic support for Let's Encrypt, but not automatic certificate updating.

There is also a bootstrapping problem here, as the ACME server will need to access your domain in order to verify that you own it, so you will have to create an initial [self-signed certificate](https://devcenter.heroku.com/articles/ssl-certificate-self) when you first configure a domain for use with API Gateway.

Then, you can generate your Let's Encrypt challenge information using a local client or a service like [GetHTTPSForFree.com](https://gethttpsforfree.com/).

Next, in your remote settings file, define the following entries (change these values, obviously):

```python
LETS_ENCRYPT_CHALLENGE_PATH = "KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz"
LETS_ENCRYPT_CHALLENGE_CONTENT = "KkI_AMwzmQxlMDtaitt7eZMWEDn0t0Fsl5HjkJSPxyz.ABC5hET2fxMsBLCsQLlAVA5MLvYUnX8gEAYaXN0xI4Y"
```

Then, continue with the process and you should receive a valid Let's Encrypt Certificate for your domain. Nice!

(When creating scheduled Lambda events via API is possible, this whole process may be wrapped into the 'deploy' command. Until then, you're kind of on your own.)

#### Keeping the server warm

Lambda has a limitation that functions which aren't called very often take longer to start - sometimes up to ten seconds. However, functions that are called regularly are cached and start quickly, usually in less than 50ms. To ensure that your servers are kept in a cached state, you can [manually configure](http://stackoverflow.com/a/27382253) a scheduled task for your Zappa function that'll keep the server cached by calling it every 5 minutes. There is currently no way to configure this through API, so you'll have to set this up manually. When this ability is available via API, django-zappa will configure this automatically. It would be nice to also add support LetsEncrypt through this same mechanism.


#### Troubleshooting

Django_zappa has a lot of moving parts and it pushes lambda out of its comfort
zone, which means sometimes things break unexpectedly. If you have trouble, the
list below may help you work your way through it.

> botocore.exceptions.ClientError: An error occurred (InvalidClientTokenId)
when calling the CreateRole operation: The security token included in the
request is invalid.

Your credentials are incorrect. Double check that you created the
~/.aws/credentials file, made it readable, and included the correct
credentials. If all of that looks right, ensure you did NOT wrap your
credentials in quotes.

> botocore.exceptions.NoRegionError: You must specify a region.

This appears to only happen for some users. There is a fix currently
in the works.

> botocore.exceptions.ClientError: An error occurred
(InvalidParameterValueException) when calling the CreateFunction operation:
Error occurred while GetObject. S3 Error Code: NoSuchKey. S3 Error Message:
The specified key does not exist.

s3 failed to reach your deployment bucket. boto sucks if your bucket
isn't in the 'US-Standard' region -- try re-creating the bucket in the
'US-Standard' region.

> botocore.exceptions.ClientError: An error occurred
(InvalidParameterValueException) when calling the CreateFunction operation:
Error occurred while GetObject. S3 Error Code: PermanentRedirect. S3 Error
Message: The bucket you are attempting to access must be addressed using the
specified endpoint. Please send all future requests to this endpoint.

Sometimes boto has trouble dealing with regions. Try using region
us-east-1 for all of your configuration and services as a workaround until
a better solution can be deployed.

> botocore.exceptions.ClientError: An error occurred
(ResourceConflictException) when calling the CreateFunction operation:
Function already exist: xxx

You already have a lambda function with this name - this can happen if
something goes wrong during a deployment or if you accidentally re-used your
project name. Go delete the offending function or change the name of your
project.


## TODO

This project is very young, so there is still plenty to be done. Contributions are more than welcome! Please file tickets before submitting patches, and submit your patches to the 'dev' branch.

Things that need work right now:

* Testing!
* Feedback!
* Real documentation / website!
