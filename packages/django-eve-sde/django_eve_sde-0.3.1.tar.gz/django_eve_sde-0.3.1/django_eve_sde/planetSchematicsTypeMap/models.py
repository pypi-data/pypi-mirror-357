from django.db import models


class PlanetSchematicsTypeMap(models.Model):
    pk = models.CompositePrimaryKey('schematicID', 'typeID')
    schematic_id = models.IntegerField(db_column='schematicID')  # Field name made lowercase.
    type_id = models.IntegerField(db_column='typeID')  # Field name made lowercase.
    quantity = models.IntegerField(blank=True, null=True)
    is_input = models.BooleanField(db_column='isInput', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'planetSchematicsTypeMap'