import requests
import bz2
import subprocess
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Updates SDE from Fuzzworks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Downloading Postgres dump of Eve SDE...'))

        # Download the dump
        r = requests.get('https://www.fuzzwork.co.uk/dump/postgres-latest.dmp.bz2')
        open('postgres-latest.dmp.bz2', 'wb').write(r.content)

        # Extract the dump
        self.stdout.write(self.style.NOTICE('Extracting Postgres dump of Eve SDE...'))
        zipfile = bz2.BZ2File('postgres-latest.dmp.bz2')
        data = zipfile.read()
        postgres_dmp = 'postgres-latest.dmp'
        open(postgres_dmp, 'wb').write(data)
        zipfile.close()

        # See which apps are installed and populate those tables
        sde_tables = []
        for app in settings.INSTALLED_APPS:
            if app.startswith('django_eve_sde.'):
                sde_tables.append(app.split('.')[1])

        # Loop through tables and drop then import the real table
        for table in sde_tables:
            self.stdout.write(self.style.NOTICE('Processing {table}...'.format(table=table)))
            # Create Commands
            drop_command = [
                'psql',
                f'--host={settings.DATABASES["default"]["HOST"]}',
                f'--username={settings.DATABASES["default"]["USER"]}',
                f'--port={settings.DATABASES["default"]["PORT"]}',
                '--no-password',
                '--quiet',
                f'--dbname={settings.DATABASES["default"]["NAME"]}',
                f'--command=drop table \"{table}\"'
            ]

            import_command = [
                'pg_restore',
                f'--host={settings.DATABASES["default"]["HOST"]}',
                f'--username={settings.DATABASES["default"]["USER"]}',
                f'--port={settings.DATABASES["default"]["PORT"]}',
                '--no-password',
                f'--dbname={settings.DATABASES["default"]["NAME"]}',
                f'--table={table}',
                '--no-owner',
                'postgres-latest.dmp'
            ]

            if os.name == 'nt':
                self.stdout.write(self.style.NOTICE('\tDroping {table}...'.format(table=table)))
                subprocess.run(args=drop_command, shell=False)
                self.stdout.write(self.style.NOTICE('\tImporting {table}...'.format(table=table)))
                subprocess.run(args=import_command, shell=False)
            else:
                self.stdout.write(self.style.NOTICE('Droping {table}...'.format(table=table)))
                subprocess.run(args=drop_command, shell=True, env={
                    'PGPASSWORD': settings.DATABASES['default']['PASSWORD']
                })
                self.stdout.write(self.style.NOTICE('Importing {table}...'.format(table=table)))
                subprocess.run(args=import_command, shell=True, env={
                    'PGPASSWORD': settings.DATABASES['default']['PASSWORD']
                })

        # Delete the files
        os.remove('postgres-latest.dmp.bz2')
        os.remove('postgres-latest.dmp')
