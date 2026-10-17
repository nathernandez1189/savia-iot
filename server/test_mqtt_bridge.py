import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mqtt_bridge import acceptable_payload


class BridgePayloadTest(unittest.TestCase):
    def test_accepts_only_small_version_two_objects(self):
        self.assertTrue(acceptable_payload(b'{"v":2,"boot":"ABC"}'))
        self.assertFalse(acceptable_payload(b'{"v":1}'))
        self.assertFalse(acceptable_payload(b'{invalid'))
        self.assertFalse(acceptable_payload(b'[]'))
        self.assertFalse(acceptable_payload(b' ' * 4097))


if __name__ == "__main__":
    unittest.main()
