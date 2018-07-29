from sysver_interactions import Interactions


class SystemVerification(Interactions):

    def __init__(self, title):
        super().__init__()
        self.set_title(title)
        self.make_layout()


SystemVerification(title="System Verification App - LSST SQuaSH")
