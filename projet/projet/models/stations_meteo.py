from django.db import models

#Informations concernant la station qui fait les relevés (id_poste, longitude, lattitude, altitude...)
class Station_poste(models.Model):
    id_post = models.CharField(max_length= 8,primary_key=True)
    post_name = models.CharField(max_length = 100)
    post_open = models.BooleanField()
    post_type = models.IntegerField()
    post_long = models.FloatField()
    post_lati = models.FloatField()
    post_alti = models.FloatField()
    post_publi = models.BooleanField()

    class Meta:
        db_table = 'station_poste'

    # def __str__(self):
    #     return str(self.post_name)

#Relevés meteorologiques d'un poste de station 
class Station_meteo(models.Model):
    id_post = models.ForeignKey(Station_poste, on_delete=models.CASCADE)
    haut_prec_RR = models.FloatField(null=True)
    duree_prec_DRR = models.FloatField(null=True)
    haut_prc1_RR1 = models.FloatField(null=True)
    evap_mont_ETPMON = models.FloatField(null=True)
    date_relv = models.IntegerField(null=True)
    temp_mini_TN = models.FloatField(null=True)
    temp_maxi_TX = models.FloatField(null=True)
    temp_moye_TM = models.FloatField(null=True)
    temp_moy_TMNX = models.FloatField(null=True)
    heur_temp_mini_TN = models.FloatField(null=True)
    heur_temp_maxi_TX = models.FloatField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['id_post']),
            models.Index(fields=['date_relv'], name='date_du_releve')
        ]
        db_table = 'station_meteo'

    def __str__(self):
        return self.id_post, self.date_relv
    
