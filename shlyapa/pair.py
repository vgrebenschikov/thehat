class Pair(object):
    def __init__(self, index_explaining=None, index_guessing=None):
        self.explaining = int(index_explaining) if index_explaining is not None else None
        self.guessing = int(index_guessing) if index_guessing is not None else None

    def __eq__(self, other):
        return self.explaining == other.explaining and self.guessing == other.guessing

    def __ne__(self, other):
        return not self == other

