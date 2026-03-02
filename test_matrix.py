import sys
import os
sys.path.append(os.getcwd())
from core.config import config
print("Matrix:", config.get_governance_matrix())
