from django import forms
from django.contrib.auth.models import User
from .models import Commande, LigneCommande

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

# Formulaire pour Commande (sans produit et quantite)
class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['adresse', 'telephone', 'statut']
        widgets = {
            'adresse': forms.TextInput(attrs={'placeholder': 'Adresse de livraison'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Numéro de téléphone'}),
        }

# Formulaire pour LigneCommande (store produit + quantite)
class LigneCommandeForm(forms.ModelForm):
    class Meta:
        model = LigneCommande
        fields = ['produit', 'quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={'min': 1}),
        }
