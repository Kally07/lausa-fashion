from .models import Categorie
from store.domain.services import get_panier_count

def categories_globales(request):
    return {
        'categories': Categorie.objects.all()
    }
# store/context_processors.py

def panier_count(request):
    return {
        'panier_count': get_panier_count(request.user)
    }
