# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Area(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)


class Tariff(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT)


class UserConsumption(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    datetime = models.DateTimeField(db_index=True)
    value = models.FloatField()

    class Meta:
        unique_together = (("user", "datetime"),)
