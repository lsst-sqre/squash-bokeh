from sysver_interactions import Interactions


class SystemVerification(Interactions):

    def __init__(self, title):
        super().__init__()
        self.set_title(title)


SystemVerification(title="System Verification App - LSST SQuaSH")
