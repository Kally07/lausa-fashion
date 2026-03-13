from django.urls import path
from dashboard.views import index, produits, commandes, categories, sous_categories, livraisons, utilisateurs, clients, livreurs, paiement, historiques

app_name = "dashboard"

urlpatterns = [
    
    # =========================
    # DASHBOARD HOME
    # =========================
    path("", utilisateurs.index, name="index"),
    path("dashboard/", index.dashboard_view, name="dashboard"),

    # =========================
    # UTILISATEURS
    # =========================
    path("utilisateurs/", utilisateurs.utilisateurs_liste, name="utilisateurs_liste"),
    path("utilisateurs/<str:utilisateur_id>/supprimer/", utilisateurs.utilisateurs_supprimer, name="utilisateur_supprimer"),
    path('utilisateurs/creer/', utilisateurs.utilisateur_creer, name='utilisateur_creer'), 
    path('utilisateurs/<str:utilisateur_id>/modifier/',utilisateurs.utilisateur_modifier, name='utilisateur_modifier'),
    path('utilisateurs/<str:utilisateur_id>/supprimer/', utilisateurs.utilisateurs_supprimer, name='utilisateur_supprimer'),
    
    # =========================
    # CLIENTS
    # =========================
    path("clients/", clients.clients_liste, name="clients_liste"),
    path("clients/creer/", clients.client_creer, name="clients_creer"),
    path("clients/<str:client_id>/supprimer", clients.clients_supprimer, name="clients_supprimer"),

    # =========================
    # LIVREURS
    # =========================
    path("livreurs/", livreurs.livreurs_liste, name="livreurs_liste"),
    path("livreurs/creer/", livreurs.livreur_creer, name="livreurs_creer"),
    path("livreurs/<str:livreur_id>/supprimer", livreurs.livreurs_supprimer, name="livreurs_supprimer"),
    # =========================
    # LIVREURS
    # =========================
    path('livreurs/', livreurs.livreurs_liste, name='livreurs_liste'),
    path('livreurs/creer/', livreurs.livreur_creer, name='livreur_creer'),
    path('livreurs/associer/', livreurs.livreur_associer, name='livreur_associer'),
    path('livreurs/<str:livreur_id>/modifier/', livreurs.livreurs_modifier, name='livreurs_modifier'),
    path('livreurs/<str:livreur_id>/supprimer/', livreurs.livreurs_supprimer, name='livreurs_supprimer'),

    # PRODUITS
    path("produits/", produits.liste_produits, name="produits_liste"),
    path("produits/creer/", produits.produits_creer, name="produits_creer"),
    path("produits/<str:produit_id>/modifier/", produits.produits_modifier, name="produits_modifier"),
    path("produits/<str:produit_id>/supprimer/", produits.produits_supprimer, name="produits_supprimer"),

    # CATEGORIES
    path("categories/", categories.liste_categories, name="categories_liste"),
    path("categories/creer/", categories.categories_creer, name="categories_creer"),
    path('categories/<str:categorie_id>/modifier/', categories.categories_modifier, name="categories_modifier"),

    # SOUS-CATEGORIES
    path("sous_categories/", sous_categories.liste_sous_categories, name="sous_categories_liste"),
    path("sous_categories/creer/", sous_categories.sous_categories_creer, name="sous_categories_creer"),
    path('sous_categories/<str:sous_categorie_id>/modifier/', sous_categories.sous_categories_modifier, name="sous_categories_modifier"),
    path('ajax/sous_categories/<str:categorie_id>/', produits.ajax_sous_categories, name='ajax_sous_categories'),

    # COMMANDES# COMMANDES
    path("commandes/", commandes.commandes_liste, name="commandes_liste"),
    path("commandes/en-attente/", commandes.commandes_en_attente, name="commandes_en_attente"),
    path("commandes/validees/", commandes.commandes_validees, name="commandes_validees"),
    path("commandes/annulees/", commandes.commandes_annulees, name="commandes_annulees"),
    path("commandes/rechercher/", commandes.commandes_rechercher, name="commandes_rechercher"),
    path("commandes/creer/", commandes.commandes_creer, name="commandes_creer"),
    path("commandes/<str:commande_id>/modifier/", commandes.commandes_modifier, name="commandes_modifier"),
    path("commandes/<str:commande_id>/supprimer/", commandes.commandes_supprimer, name="commandes_supprimer"),
    path("commandes/<str:commande_id>/valider/", commandes.commandes_valider, name="commandes_valider"),
    path("commandes/<str:commande_id>/annuler/", commandes.commandes_annuler, name="commandes_annuler"),
    
    # =========================
    # PAIEMENT
    # =========================
    path("paiements/", paiement.liste_paiements, name="paiements_liste"),
    
    # =========================
    # HISTORIQUES
    # =========================
    path("historiques/", historiques.historiques_liste, name="historique_actions"),

    # LIVRAISONS
    path("livraisons/", livraisons.livraisons_liste, name="livraisons_liste"),
    # Liste des livraisons
    path("livraisons/", livraisons.livraisons_liste, name="livraisons_liste"),
    # Créer une livraison
    path("livraisons/creer/", livraisons.livraisons_creer, name="livraisons_creer"),
    # Terminer une livraison
    path("livraisons/<str:livraison_id>/terminer/", livraisons.livraisons_terminer, name="livraisons_terminer"),
]
