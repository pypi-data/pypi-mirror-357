from django.db import models


class InvGroup(models.Model):
    group_id = models.IntegerField(db_column='groupID', primary_key=True)  # Field name made lowercase.
    category_id = models.IntegerField(db_column='categoryID', blank=True, null=True)  # Field name made lowercase.
    group_name = models.CharField(db_column='groupName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    icon_id = models.IntegerField(db_column='iconID', blank=True, null=True)  # Field name made lowercase.
    use_base_price = models.BooleanField(db_column='useBasePrice', blank=True, null=True)  # Field name made lowercase.
    anchored = models.BooleanField(blank=True, null=True)
    anchorable = models.BooleanField(blank=True, null=True)
    fittable_nonsingleton = models.BooleanField(db_column='fittableNonSingleton', blank=True, null=True)  # Field name made lowercase.
    published = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'invGroups'