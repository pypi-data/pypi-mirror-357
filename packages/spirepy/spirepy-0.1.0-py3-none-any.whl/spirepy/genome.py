from spirepy import Sample


class Genome:
    """
    A genome from SPIRE.
    """

    def __init__(self, id: str, sample: Sample):
        """
        Creates a new genome instance.
        """
        self.id = id
        self.sample = sample
        self._abundance = None
