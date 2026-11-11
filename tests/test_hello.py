import unittest, subprocess, sys


class T(unittest.TestCase):
    def test_hello(self):
        out = subprocess.run([sys.executable, "app/hello.py"], capture_output=True, text=True).stdout
        self.assertIn("Pollie", out)


if __name__ == "__main__":
    unittest.main()
