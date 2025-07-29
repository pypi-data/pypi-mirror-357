"Can be found in gpkit/docs/source/examples/external_sp.py"

import numpy as np

# pylint: disable=import-error
from external_constraint import ExternalConstraint

from gpkit import Model, Variable

x = Variable("x")
y = Variable("y")

objective = y

constraints = [
    ExternalConstraint(x, y),
    x <= np.pi / 2,
    x >= np.pi / 4,
]

m = Model(objective, constraints)
print(m.localsolve(verbosity=0).summary())
