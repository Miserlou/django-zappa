# Contributing Guide [![badge](https://img.shields.io/badge/Django-CC-ee66dd.svg)][django-cc]
This project follows the **[Django Contributing Commons][django-cc]**.

## Getting started
Getting started is simple, just do:
```bash
pip install dcc
dcc django-zappa
hub checkout -b patch-1
```

To test locally simply run:
```bash
tox
```

After that just write your code. Once you are done, just follow this easy flow:
```bash
hub commit
hub pull-request -b Miserlou
```

[django-cc]: https://github.com/codingjoe/django-cc/blob/master/CONTRIBUTING.md
