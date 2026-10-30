from django.db import models

# Create your models here.
from django.db.models import CASCADE


class ClientRegister_Model(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=10)
    phoneno = models.CharField(max_length=10)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    status = models.CharField(max_length=20, default='waiting')


class predict_climate_change_impact(models.Model):

    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)
    Elevation = models.FloatField(null=True, blank=True)
    AverageTemperature = models.FloatField(null=True, blank=True)
    AnnualPrecipitation = models.FloatField(null=True, blank=True)
    SoilPH = models.FloatField(null=True, blank=True)
    SoilOrganicCarbon = models.FloatField(null=True, blank=True)
    ClayContent = models.FloatField(null=True, blank=True)

    Prediction = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.Prediction)


class detection_accuracy(models.Model):

    names = models.CharField(max_length=300)
    ratio = models.CharField(max_length=300)

class detection_ratio(models.Model):

    names = models.CharField(max_length=300)
    ratio = models.CharField(max_length=300)



