"""
🧠 review_generator.py
Génère automatiquement des avis produits à partir d'informations basiques, pour usage avec Amazon Affiliates.

"""

import random

# Exemples de templates (à enrichir dynamiquement plus tard)
TEMPLATES = [
    "J'ai récemment découvert le {product_name} et je dois dire que c'est {adjective}. Il offre {feature} avec une qualité remarquable. Un excellent choix si vous cherchez {benefit}.",
    "Le {product_name} m'a surpris par sa {feature}. C'est un produit {adjective}, parfait pour {benefit}. À recommander !",
    "{product_name} est vraiment {adjective}. Il se distingue par {feature}. Je l'utilise pour {benefit}, et j'en suis très satisfait.",
]

ADJECTIVES = ["exceptionnel", fiable", "abordable", "intelligent", "pratique", "très utile"]
FEATURES = ["une autonomie remarquable", "une ergonomie bien pensée", "des performances fluides", "une solidité à toute épreuve"]
BENEFITS = ["gagner du temps", "travailler efficacement", "améliorer mon quotidien", "optimiser mon espace de travail"]

def generate_review(product_name):
    adjective = random.choice(ADJECTIVES)
    feature = random.choice(FEATURES)
    benefit = random.choice(BENEFITS)
    template = random.choice(TEMPLATES)

    return template.format(
        product_name=product_name,
        adjective=adjective,
        feature=feature,
        benefit=benefit
    )

# Exemple d’utilisation
if __name__ == "__main__":
    product = "Support d'écran ergonomique"
    print(generate_review(product))
