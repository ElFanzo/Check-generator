from django.contrib.postgres.fields import JSONField
from django.db import models


class Printer(models.Model):
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100)
    check_type = models.CharField(max_length=30)
    point_id = models.IntegerField()

    def __str__(self):
        return f"{self.check_type} Printer for {self.point_id} point"


class Check(models.Model):
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, related_name="checks")
    type = models.CharField(max_length=30)
    order = JSONField()
    status = models.CharField(max_length=30)
    pdf_file = models.FileField(upload_to="pdf/", null=True, blank=True)

    def __str__(self):
        return f"{self.status} Check for ({self.printer})"
