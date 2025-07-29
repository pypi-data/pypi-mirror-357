def test_analyse_donnees():
    from affiliate_ai.modules import analyse_revenus
    analyse_revenus.analyser_revenus_vs_publications()
    assert True  # Si pas d’erreur, test OK
