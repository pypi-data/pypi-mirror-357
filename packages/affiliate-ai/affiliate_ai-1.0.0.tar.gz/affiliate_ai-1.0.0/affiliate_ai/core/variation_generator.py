"""
variation_generator.py – Génère des variantes d’un texte pour éviter le spam/flood
"""

import random

def varier_contenu(original):
    synonymes = {
        "excellent": ["remarquable", "très bon", "impressionnant", "hautement recommandé"],
        "produit": ["article", "objet", "élément", "matériel"],
        "je recommande": ["je suggère", "je conseille", "vous devriez essayer", "c’est une bonne pioche"],
        "vraiment": ["absolument", "clairement", "vraiment bien", "sans hésiter"],
        "facile": ["simple", "intuitif", "sans prise de tête", "accessible"],
    }

    contenu = original
    for mot, variantes in synonymes.items():
        if mot in contenu:
            contenu = contenu.replace(mot, random.choice(variantes), 1)

    # Variation structurelle
    if random.random() > 0.5:
        contenu += "

En tout cas, c’est mon avis perso. À vous de voir ! 😉"
    else:
        contenu = "🔍 Voici mon retour d’expérience :

" + contenu

    return contenu
