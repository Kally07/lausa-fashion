from store.domain.exceptions import PaiementInvalideError

def valider_paiement_natcash(reference: str, montant: float):
    """
    Vérifie le paiement via NatCash.
    À remplacer par un vrai appel API NatCash.
    """
    # TODO: appel réel API NatCash ici
    success = True  # simulation
    if not success:
        raise PaiementInvalideError(f"Paiement NatCash {reference} invalide")
    return True
