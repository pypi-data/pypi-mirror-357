import tarfile
import tempfile
import os.path as path
import os
import urllib

import polars as pl

from spirepy.logger import logger
from spirepy.data import genome_metadata


class Study:
    """
    A study from SPIRE.

    This class represents a study from the SPIRE database. It automatically
    fetches metadata and automates the initialization of samples to further use
    to obtain its genomic, geographical or other types of data provided by it.

    Attributes:

    name: str
        Internal ID for the study.
    """

    def __init__(self, name: str):
        self.name = name
        self._metadata = None
        self._samples = None
        self._mags = None

    def get_metadata(self):
        """Retrieve metadata for the study."""
        if self._metadata is None:
            study_meta = pl.read_csv(
                f"https://spire.embl.de/api/study/{self.name}?format=tsv",
                separator="\t",
            )
            self._metadata = study_meta
        return self._metadata

    def get_samples(self):
        """Retrive samples for the study."""
        from spirepy.sample import Sample

        if self._samples is None:
            sample_list = []
            for s in self.get_metadata()["sample_id"].to_list():
                sample = Sample(s, self)
                sample_list.append(sample)
            self._samples = sample_list
        return self._samples

    def get_mags(self):
        """Get a DataFrame with information regarding the MAGs."""
        if self._mags is None:
            genomes = genome_metadata()
            self._mags = genomes.filter(
                genomes["derived_from_sample"].is_in(
                    self.get_metadata()["sample_id"].to_list()
                )
            )
        return self._mags

    def download_mags(self, output: str):
        """Download the MAGs into a specified folder.

        Parameters:

        output: str
            Output folder to download the MAGs to.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tarfpath = path.join(tmpdir, f"{self.name}_mags.tar")
            urllib.request.urlretrieve(
                f"https://swifter.embl.de/~fullam/spire/compiled/{self.name}_spire_v1_MAGs.tar",
                tarfpath,
            )
            os.makedirs(output, exist_ok=True)
            with tarfile.open(tarfpath) as tar:
                tar.extractall(path.join(output, "mags"))
