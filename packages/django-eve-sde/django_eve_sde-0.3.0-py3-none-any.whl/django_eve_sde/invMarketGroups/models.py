from django.db import models


class InvMarketGroup(models.Model):
    market_group_id = models.IntegerField(db_column='marketGroupID', primary_key=True)  # Field name made lowercase.
    parent_group_id = models.IntegerField(db_column='parentGroupID', blank=True, null=True)  # Field name made lowercase.
    market_group_name = models.CharField(db_column='marketGroupName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True, null=True)
    icon_id = models.IntegerField(db_column='iconID', blank=True, null=True)  # Field name made lowercase.
    has_types = models.BooleanField(db_column='hasTypes', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'invMarketGroups'