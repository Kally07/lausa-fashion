from django.db import models

class Sequence(models.Model):
    prefix = models.CharField(max_length=4)
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    last_value = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('prefix', 'year', 'month')

    def __str__(self):
        return f"{self.prefix}-{self.year}{self.month} → {self.last_value}"
