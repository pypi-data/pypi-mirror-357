import unittest
import json
from pathlib import Path
from datetime import datetime
from affiliate_ai.cli import ajouter_planification

class TestPlanification(unittest.TestCase):
    def test_ajout_planification(self):
        today = datetime.now().strftime("%Y-%m-%d")
        ajouter_planification(today)
        plan = json.loads(Path("affiliate_ai/db/planifications.json").read_text())
        self.assertTrue(any(p['date'] == today for p in plan))

if __name__ == '__main__':
    unittest.main()
