import copy, os, sys, unittest
sys.path.insert(0, os.path.dirname(__file__))
import validate_pack as vp


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = vp.load(os.path.join(vp.ROOT, "data"))

    def test_clean_pack_passes(self):
        self.assertEqual(vp.validate(self.d), [])

    def test_detects_count_change(self):
        d = copy.deepcopy(self.d); d["enemies"].pop()
        self.assertTrue(any("enemies" in e for e in vp.validate(d)))

    def test_detects_disconnected_dungeon(self):
        d = copy.deepcopy(self.d); d["dungeons"][0]["connections"] = d["dungeons"][0]["connections"][:1]
        self.assertTrue(any("disconnected" in e for e in vp.validate(d)))

    def test_detects_cycle(self):
        d = copy.deepcopy(self.d); d["chapters"][0]["prerequisites"] = ["CH24"]
        self.assertTrue(any("cycle" in e for e in vp.validate(d)))

    def test_detects_bad_boss_ref(self):
        d = copy.deepcopy(self.d); d["dungeons"][3]["boss"] = "B99"
        self.assertTrue(any("boss ref" in e for e in vp.validate(d)))


if __name__ == "__main__":
    unittest.main()
