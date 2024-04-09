from django.db import models

class Watercourse(models.Model):
    name = models.CharField(max_length=200)
    watercourse_code = models.CharField(max_length=100, unique=True)
    length = models.FloatField()
    first_point = models.JSONField()
    last_point = models.JSONField()
    is_affluent = models.BooleanField()
    classe = models.FloatField()
    river_join= models.CharField(max_length=200, null=True)


    

    class Meta:
        db_table = 'watercourse'
