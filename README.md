![Real logo coming soon..](https://i.imgur.com/wZ4WVnm.png)

# django-zappa
#### Django on AWS Lambda with API Gateway

To use other WSGI apps on AWS Lambda, use the Zappa library on which this depends.

[See in action here!](https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/prod)

## Status

**It works!** Django on AWS Lambda with API Gateway! Woo!

### TODO
  - Automatic deployment tools
  - POST/PUT/etc.
  - Use databases
  - Pretty much everything else.
  - Tests

## Installation

(This doesn't work.. yet..)

    $ pip install django-zappa

## Basic Usage

Since you deploy zappa from your local machine's bundle, you'll have to define a zappa_settings.py. This is just like a normal settings.py, but configured with your production AWS database information.

Also, make sure you have your AWS API keys set up.

Finally..

    $ python manage.py zappa deploy

Or, to just stage it but not activate it..

    $ python manage.py zappa stage

## Advanced Usage

All of the settings have sane defaults, but you can also override the Zappa-specific settings.

    ZAPPA_FOO = "BAR"
