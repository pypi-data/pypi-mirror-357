from django.db import models


class InvCategory(models.Model):
    category_id = models.IntegerField(db_column='categoryID', primary_key=True)  # Field name made lowercase.
    category_name = models.CharField(db_column='categoryName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    icon_id = models.IntegerField(db_column='iconID', blank=True, null=True)  # Field name made lowercase.
    published = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'invCategories'