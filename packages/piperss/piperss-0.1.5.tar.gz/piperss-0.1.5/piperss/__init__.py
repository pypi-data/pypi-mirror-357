import sys
import os

vendor_dir = os.path.join(os.path.dirname(__file__), "vendor")
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)
