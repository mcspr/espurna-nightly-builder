import unittest

from espurna_nightly_builder import rename_releases


class TestVersionSub(unittest.TestCase):

    FILE = "espurna-1.13.4-dev-itead-sonoff-basic.bin"
    MASK = "espurna-1.13.4-dev"

    def test_replace_version(self):
        expect = self.FILE.replace("1.13.4-dev", "1.13.5")

        res = rename_releases.version_sub(
            self.FILE, self.MASK, "{version}", version="1.13.5"
        )
        self.assertEqual(res, expect)

    def test_keep_version(self):
        res = rename_releases.version_sub(
            self.FILE, self.MASK, "{orig_version}", version="1.13.5"
        )
        self.assertEqual(self.FILE, res)

    def test_mask_no_match(self):
        filename = "memory.map"
        res = rename_releases.version_sub(
            filename, self.MASK, "{version}", version="1.13.5"
        )
        self.assertEqual(filename, res)


if __name__ == "__main__":
    unittest.main()
