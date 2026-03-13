from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import Utilisateur


# =====================================================
# INSCRIPTION UTILISATEUR (COMPTE SIMPLE)
# =====================================================

class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = Utilisateur
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        """
        Crée UNIQUEMENT l'utilisateur.
        Le profil client sera créé plus tard via devenir_client().
        """
        utilisateur = super().save(commit=False)

        utilisateur.role = "client"
        utilisateur.statut = "actif"
        utilisateur.is_active = True

        if commit:
            utilisateur.save()

        return utilisateur


# =====================================================
# FORMULAIRE DEVENIR CLIENT
# =====================================================

class DevenirClientForm(forms.Form):
    nom = forms.CharField(max_length=50)
    prenom = forms.CharField(max_length=50)
    telephone = forms.CharField(max_length=20, required=False)
    adresse = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )


# =====================================================
# CONNEXION
# =====================================================

class ConnexionForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Mot de passe"
    )
