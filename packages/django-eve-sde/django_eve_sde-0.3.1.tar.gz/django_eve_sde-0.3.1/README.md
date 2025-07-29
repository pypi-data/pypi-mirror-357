# Django Eve SDE
Only supports Postgres databases for now, if using Docker you have to install the 
cli tools for postgres.

If on windows you'll need to make sure you have a postgres password file as described here https://www.postgresql.org/docs/current/libpq-pgpass.html

```shell
apt-get install -y --no-install-recommends postgresql-client
```

## Installation

```shell
pip install git+https://github.com/timthedevguy/django_eve_sde.git
```
or
```shell
poetry add git+https://github.com/timthedevguy/django_eve_sde.git
```

## What this does

This module will download the SDE dump files, and then import only the tables you need based on what gets added to ```INSTALLED_APPS```.
This saves space as you aren't storing the entirety of Eve SDE in your database, only
the tables you need to use.

Tables available are under the ```django_eve_sde``` module.

For example, to use the invTypes table add the following to your ```INSTALLED_APPS``` in settings.py

```python
INSTALLED_APPS = [
    ...,
    ...,
    "django_eve_sde",  # Always import django_eve_sde if you have at least one table  import
    "django_eve_sde.invTypes"
]
```

Now run
```shell
python ./manage.py update_sde
```

The Postgres SDE dump will be downloaded and the correct table will be imported
to your ```default``` database.

You can now use the model just like your own models by importing them

```python
from django_eve_sde.invTypes.models import InvType
```
Looking up an item
```python
item = InvType.objects.filter(type_id=34)
```