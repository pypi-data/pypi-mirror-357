from django.db import models
from django_eve_sde import INDUSTRY_ACTIVITY_CHOICES


class IndustryActivity(models.Model):
    pk = models.CompositePrimaryKey('typeID', 'activityID')
    type_id = models.IntegerField(db_column='typeID')  # Field name made lowercase.
    activity_id = models.IntegerField(db_column='activityID', choices=INDUSTRY_ACTIVITY_CHOICES)  # Field name made lowercase.
    time = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'industryActivity'