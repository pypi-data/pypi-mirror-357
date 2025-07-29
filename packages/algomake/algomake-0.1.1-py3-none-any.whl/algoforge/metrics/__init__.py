# algoforge/metrics/__init__.py

# Import sub-modules to make them accessible via the package namespace
from . import classification
from . import regression

# Optionally, you can also import specific functions directly into the metrics namespace
# to allow users to do `from algoforge.metrics import accuracy_score`
from .classification import accuracy_score, confusion_matrix
from .regression import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score