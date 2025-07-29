# django-hstore-field


[![Downloads](https://static.pepy.tech/badge/django-hstore-field)](https://pepy.tech/project/django-hstore-field)  [![CI](https://github.com/baseplate-admin/django-hstore-field/actions/workflows/CI.yml/badge.svg)](https://github.com/baseplate-admin/django-hstore-field/actions/workflows/test.yml) [![Pypi Badge](https://img.shields.io/pypi/v/django-hstore-field.svg)](https://pypi.org/project/django-hstore-field/) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/baseplate-admin/django-hstore-field/master.svg)](https://results.pre-commit.ci/latest/github/baseplate-admin/django-hstore-field/master)

An easy to use postgres [hstore](www.postgresql.org/docs/current/hstore.html) field that is based on [`django-hstore-widget`](https://github.com/baseplate-admin/django-hstore-widget)

## Requirements

-   Python 3.9 and Up ( well technically any python version from 3.6 should work )
-   Django 3.2 and Up
-   Modern browsers ( Chrome 112+, Firefox 117+, Safari 16.5+ )

```bash
pip install django-hstore-field
```

## Installation

### Option 1:

Include [`django-hstore-widget`](https://github.com/baseplate-admin/django-hstore-widget) in your `settings.py`:

```python

# settings.py

INSTALLED_APPS = [
    ...,
    'django_hstore_widget',
    ...
]

```


### Option 2:

Include  `django_hstore_widget`'s migration to any of your model


```python
# Generated migration file
from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):
    dependencies = [
        ("django_hstore_widget", "__latest__"),
    ]

    operations = [
        # any operations
    ]

```


## Usage

```python
# yourapp/models.py
from django.db import models
from django_hstore_field import HStoreField


class ExampleModel(models.Model):
    data = HStoreField()
```
