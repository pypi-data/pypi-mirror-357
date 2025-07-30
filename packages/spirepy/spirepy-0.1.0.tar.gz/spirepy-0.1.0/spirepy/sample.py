import os
import os.path as path
import urllib.request

import polars as pl
import pandas as pd

from spirepy.logger import logger
from spirepy.data import cluster_metadata
from spirepy.study import Study


class Sample:
    """
    A sample from SPIRE.

    This class represents a sample from the SPIRE database. It is designed to
    provide all the properties and methods to allow work with samples and
    provide tools for automation and scalability.

    Attributes:

    id: str
        Internal ID for the sample.
    study: Study
        Study ID to which the sample belongs to.
    """

    def __init__(self, id: str, study: Study = None):
        """
        Creates a new sample object.
        """
        self.id = id
        self.study = study
        self._metadata = None
        self._manifest = None
        self._mags = None
        self._eggnog_data = None
        self._amr_annotations = None

    def __str__(self):
        return f"Sample id: {self.id} \tStudy: {[self.study.name if type(self.study) is Study else None]}"

    def __repr__(self):
        return self.__str__()

    def get_metadata(self):
        """Retrieve the metadata for a sample."""
        if self._metadata is None:
            sample_meta = pl.read_csv(
                f"https://spire.embl.de/api/sample/{self.id}?format=tsv", separator="\t"
            )
            self._metadata = sample_meta
        return self._metadata

    def get_mags(self):
        """Retrieve the MAGs for a sample."""
        if self._mags is None:
            cluster_meta = cluster_metadata()
            clusters = self.get_metadata().filter(
                self.get_metadata()["spire_cluster"] != "null"
            )
            mags = cluster_meta.filter(
                cluster_meta["spire_cluster"].is_in(clusters["spire_cluster"])
            )
            mags = mags.join(clusters, on="spire_cluster")
            mags = mags.select(
                pl.col("spire_id"),
                pl.col("sample_id"),
                pl.all().exclude(["spire_id", "sample_id"]),
            )
            self._mags = mags
        return self._mags

    def get_eggnog_data(self):
        """Retrive the EggNOG-mapper data for a sample."""
        if self._eggnog_data is None:
            egg = pd.read_csv(
                f"https://spire.embl.de/download_eggnog/{self.id}",
                sep="\t",
                skiprows=4,
                skipfooter=3,
                compression="gzip",
                engine="python",
            )
            eggnog_data = pl.from_pandas(egg)
            self._eggnog_data = eggnog_data
        return self._eggnog_data

    def get_amr_annotations(self, mode: str = "deeparg"):
        """Obtain the anti-microbial resistance annotations for the sample.

        Parameters:

        mode: str
            Tool to select the AMR data from. Options are deepARG (deeparg),
            abricate-megares (megares) and abricate-vfdb (vfdb). Defaults to deepARG.
        """
        if self._amr_annotations is None:
            url = {
                "deeparg": f"https://spire.embl.de/download_deeparg/{self.id}",
                "megares": f"https://spire.embl.de/download_abricate_megares/{self.id}",
                "vfdb": f"https://spire.embl.de/download_abricate_vfdb/{self.id}",
            }.get(mode)
            if url is None:
                logger.error(
                    "Invalid option, please choose one of the following: deeparg, megares, vfdb"
                )
                return None
            amr = pl.read_csv(url, separator="\t")
            self._amr_annotations = amr
        return self._amr_annotations

    def download_mags(self, out_folder):
        """Download the MAGs into a specified folder.

        Parameters:

        output: str
            Output folder to download the MAGs to.
        """
        os.makedirs(out_folder, exist_ok=True)
        for mag in self.get_mags()["spire_id"].to_list():
            urllib.request.urlretrieve(
                f"https://spire.embl.de/download_file/{mag}",
                path.join(out_folder, f"{mag}.fa.gz"),
            )
