from django.db import models


class PlanetSchematic(models.Model):
    schematic_id = models.IntegerField(db_column='schematicID', primary_key=True)  # Field name made lowercase.
    schematic_name = models.CharField(db_column='schematicName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cycle_time = models.IntegerField(db_column='cycleTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'planetSchematics'