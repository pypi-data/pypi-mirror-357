from django.db import models


class PlanetSchematicsPinMap(models.Model):
    pk = models.CompositePrimaryKey('schematicID', 'pinTypeID')
    schematic_id = models.IntegerField(db_column='schematicID')  # Field name made lowercase.
    pin_type_id = models.IntegerField(db_column='pinTypeID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'planetSchematicsPinMap'