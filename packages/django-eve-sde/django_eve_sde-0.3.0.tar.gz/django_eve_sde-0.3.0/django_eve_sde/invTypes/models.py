from django.db import models


class InvType(models.Model):
    type_id = models.IntegerField(db_column='typeID', primary_key=True)  # Field name made lowercase.
    group_id = models.IntegerField(db_column='groupID', blank=True, null=True)  # Field name made lowercase.
    type_name = models.CharField(db_column='typeName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    mass = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    capacity = models.FloatField(blank=True, null=True)
    portion_size = models.IntegerField(db_column='portionSize', blank=True, null=True)  # Field name made lowercase.
    race_id = models.IntegerField(db_column='raceID', blank=True, null=True)  # Field name made lowercase.
    base_price = models.DecimalField(db_column='basePrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    published = models.BooleanField(blank=True, null=True)
    market_group_id = models.IntegerField(db_column='marketGroupID', blank=True, null=True)  # Field name made lowercase.
    icon_id = models.IntegerField(db_column='iconID', blank=True, null=True)  # Field name made lowercase.
    sound_id = models.IntegerField(db_column='soundID', blank=True, null=True)  # Field name made lowercase.
    graphic_id = models.IntegerField(db_column='graphicID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'invTypes'