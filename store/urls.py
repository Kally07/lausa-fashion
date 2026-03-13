from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "store"

urlpatterns = [
    # =========================
    # AUTH
    # =========================
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="store:index"), name="logout"),
    path("register/", views.register, name="register"),

    # =========================
    # PAGES STATIQUES
    # =========================
    path("", views.index, name="index"),
    path("apropos/", views.apropos, name="apropos"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
    path("profil/", views.profil_view, name="profil"),

    # =========================
    # PRODUITS
    # =========================
    path("produits/", views.liste_produits, name="liste_produits"),
    path("produit/detail/", views.detail_produit, name="detail_produit"),
    path("produits/categorie/", views.produits_par_categorie, name="produits_par_categorie"),
    path("sous-categorie/<str:sous_categorie_id>/", views.produits_sous_categorie, name="produits_sous_categorie"),

    # =========================
    # PANIER
    # =========================
    path("panier/", views.panier, name="panier"),
    path("panier/ajouter/", views.ajouter_au_panier, name="ajouter_au_panier"),
    path("panier/mise_a_jour_ajax/", views.mise_a_jour_panier_ajax, name="mise_a_jour_panier_ajax"),
    path("panier/supprimer/", views.supprimer_du_panier, name="supprimer_du_panier"),
    path("panier/vider/", views.vider_panier_view, name="vider_panier"),
    path("panier/count_ajax/", views.panier_count_ajax, name="panier_count_ajax"),

    # =========================
    # COMMANDE
    # =========================
    path("commande/valider/", views.valider_commande_view, name="valider_commande"),
    path("mes_commandes/", views.mes_commandes, name="mes_commandes"),
    path("commande/<str:commande_id>/", views.detail_commande, name="detail_commande"),

    # =========================
    # RECHERCHE
    # =========================
    path("recherche/", views.recherche, name="recherche"),

    # =========================
    # PAIEMENT
    # =========================
    path('paiement/moncash/', views.paiement_moncash_view, name='paiement_moncash'),
    path("paiement/moncash/success/", views.paiement_moncash_success, name="moncash_success"),
    path("paiement/moncash/cancel/", views.paiement_moncash_cancel, name="moncash_cancel"),

    #path("checkout/<str:panier_id>/", views.checkout_panier, name="checkout_panier"),
    #path("payer/<str:panier_id>/", views.payer_panier, name="payer_panier"),
    #path("webhook/moncash/", views.moncash_webhook, name="moncash_webhook"),

    #path('paiement/natcash/', views.paiement_natcash_view, name='paiement_natcash'),
    #path('paiement/carte/', views.paiement_carte_view, name='paiement_carte'),

    path("paiement/moncash/local/", views.paiement_moncash_local_ajax, name="paiement_moncash_local_ajax"),

]
