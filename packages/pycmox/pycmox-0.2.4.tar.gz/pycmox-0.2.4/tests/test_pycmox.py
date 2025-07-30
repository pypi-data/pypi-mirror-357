import unittest
import pycmox

class TestPycmox(unittest.TestCase):
	def test_pycmox(self):
		self.assertIsInstance(pycmox.RS485, type)
		self.assertIsInstance(pycmox.RS485.BUSY, int)
		self.assertIsInstance(pycmox.RS485.DONE, int)
		self.assertIsInstance(pycmox.RS485.NONE, int)

if __name__ == '__main__':
	unittest.main()
