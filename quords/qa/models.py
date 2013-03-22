# =====================
# qa/models.py
# =====================

from django.db import models

class Compare(models.Model):
    orig_image = models.CharField(max_length=150)
    wayback_image = models.CharField(max_length=150)

class BlankPage(models.Model):
    orig_image = models.CharField(max_length=150)

class CompareCollection(models.Model):
    seed_file = models.CharField(max_length=150)

class Photo(models.Model):
    title = models.CharField(max_length=255)
    img = models.ImageField(upload_to="orig")

    class Meta:
        verbose_name = "LiveSite"
        verbose_name_plural = "LiveSite"

    def __unicode__(self):
        return self.title
