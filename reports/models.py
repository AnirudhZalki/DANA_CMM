from django.db import models

# Create your models here.
from djongo import models

class CMMReport(models.Model):
    line = models.CharField(max_length=100)
    machine = models.CharField(max_length=100)
    part_no = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)

    oe_name = models.CharField(max_length=100)
    shift = models.CharField(max_length=10)
    remarks = models.CharField(max_length=200)
    activity = models.CharField(max_length=200)

    in_time = models.DateTimeField(null=True, blank=True)
    out_time = models.DateTimeField(null=True, blank=True)

    uploaded_from = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "CMM Report"
        verbose_name_plural = "CMM Reports"

    def __str__(self):
        return f"{self.part_no} - {self.machine}"
