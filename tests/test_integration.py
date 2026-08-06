import pytest
from streamlit.testing.v1 import AppTest
import os

def test_app_starts():
    """Test que l'application principale se lance sans erreur."""
    at = AppTest.from_file("app.py").run()
    assert not at.exception
    
def test_pages_load():
    """Test que chaque page se charge correctement."""
    pages = [
        "pages/p1_vue_globale.py",
        "pages/p2_cartographie.py",
        "pages/p3_accessibilite.py",
        "pages/p4_services.py",
        "pages/p5_temporel.py",
        "pages/p6_hierarchie.py"
    ]
    for page in pages:
        if os.path.exists(page):
            at = AppTest.from_file(page).run()
            assert not at.exception, f"Erreur dans le chargement de {page}"
