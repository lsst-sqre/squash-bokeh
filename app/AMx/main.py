from amx_interactions import Interactions

class AMx(Interactions):

    def __init__(self, title):
        super().__init__()
        self.set_title(title)

AMx(title="AMx App - LSST SQuaSH")
