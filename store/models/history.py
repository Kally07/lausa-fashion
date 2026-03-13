from django.db import models
from django.conf import settings
from store.domain.code_generator import generate_code

# =========================
# HISTORIQUE
# =========================
class Historique(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='historiques'
    )
    action = models.TextField()
    date_action = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("HIST")
        super().save(*args, **kwargs)
