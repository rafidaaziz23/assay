"""Root pytest config: force offline (cached) mode so tests never hit the network."""
import os

os.environ["DEMO_MODE"] = "cached"
