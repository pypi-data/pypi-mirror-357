from django.db import models
from django_eve_sde import INDUSTRY_ACTIVITY_CHOICES


class IndustryActivityMaterial(models.Model):
    type_id = models.IntegerField(db_column='typeID', blank=True, null=True)  # Field name made lowercase.
    activity_id = models.IntegerField(db_column='activityID', blank=True, null=True, choices=INDUSTRY_ACTIVITY_CHOICES)  # Field name made lowercase.
    material_type_id = models.IntegerField(db_column='materialTypeID', blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'industryActivityMaterials'