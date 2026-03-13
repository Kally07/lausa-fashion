from django.contrib import admin

# Register your models here.
from .models import Utilisateur, Client, Livreur

admin.site.register(Utilisateur)
admin.site.register(Client)
admin.site.register(Livreur)