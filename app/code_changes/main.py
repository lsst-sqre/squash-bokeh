import os
from interactions import Interactions

SQUASH_PY_CALL_GRAPH = os.environ.get('SQUASH_PY_CALL_GRAPH')


class Monitor(Interactions):

    def __init__(self, title):
        super().__init__()
        self.set_title(title)
        self.make_layout()


if SQUASH_PY_CALL_GRAPH:
    from pycallgraph import PyCallGraph
    from pycallgraph.output import GraphvizOutput

    with PyCallGraph(output=GraphvizOutput()):
        Monitor(title="Monitor App - LSST SQuaSH")

else:
    Monitor(title="Monitor App - LSST SQuaSH")
