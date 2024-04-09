from django.db import models

class Station(models.Model):
    code_site = models.CharField(max_length=100)
    libelle_site = models.CharField(max_length=200)
    code_station = models.CharField(max_length=100)
    libelle_station = models.CharField(max_length=200)
    type_station = models.CharField(max_length=50)
    coordonnee_x_station = models.FloatField()
    coordonnee_y_station = models.FloatField()
    code_projection = models.CharField(max_length=50)
    longitude_station = models.FloatField()
    latitude_station = models.FloatField()
    # influence_locale_station = models.FloatField(null=True, blank=True)
    commentaire_station = models.TextField(null=True, blank=True)
    altitude_ref_alti_station = models.FloatField(null=True)
    code_systeme_alti_site = models.CharField(max_length=100, null=True, blank=True)
    code_commune_station = models.CharField(max_length=100)
    libelle_commune = models.CharField(max_length=200)
    code_departement = models.CharField(max_length=50)
    code_region = models.CharField(max_length=50)
    libelle_region = models.CharField(max_length=200)
    code_cours_eau = models.CharField(max_length=100, null=True, blank=True)
    libelle_cours_eau = models.CharField(max_length=200, null=True, blank=True)
    uri_cours_eau = models.URLField(null=True, blank=True)
    descriptif_station = models.TextField(null=True, blank=True)
    date_maj_station = models.DateTimeField()
    date_ouverture_station = models.DateTimeField(null=True, blank=True)
    date_fermeture_station = models.DateTimeField(null=True, blank=True)
    commentaire_influence_locale_station = models.TextField(null=True, blank=True)
    code_regime_station = models.CharField(max_length=50)
    qualification_donnees_station = models.FloatField()
    code_finalite_station = models.CharField(max_length=100, null=True, blank=True)
    type_contexte_loi_stat_station = models.CharField(max_length=100, null=True, blank=True)
    type_loi_station = models.CharField(max_length=100, null=True, blank=True)
    code_sandre_reseau_station = models.CharField(max_length=100, null=True, blank=True)
    date_debut_ref_alti_station = models.DateTimeField(null=True, blank=True)
    date_activation_ref_alti_station = models.DateTimeField(null=True, blank=True)
    date_maj_ref_alti_station = models.DateTimeField(null=True, blank=True)
    libelle_departement = models.CharField(max_length=200)
    en_service = models.BooleanField()
    # geometry = models.JSONField()
    
    class Meta:
        db_table = 'projet_station'

    def __str__(self):
        return self.libelle_station
