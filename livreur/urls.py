
from django.urls import path
from . import views

app_name = "livreur"

urlpatterns = [

    # ============================
    # Dashboard
    # ============================
    path("index/", views.dashboard_livreur, name="index"),

    # ============================
    # Liste des livraisons
    # ============================
    path("livraisons/", views.livraisons_liste, name="livraisons_liste"),

    # ============================
    # Détail d'une livraison
    # ============================
    path(
        "livraisons/<str:livraison_id>/",
        views.livraison_detail,
        name="livraison_detail"
    ),

    # ============================
    # Modifier statut livraison
    # ============================
    path(
        "livraisons/<str:livraison_id>/modifier/",
        views.modifier_statut,
        name="modifier_statut"
    ),

]

