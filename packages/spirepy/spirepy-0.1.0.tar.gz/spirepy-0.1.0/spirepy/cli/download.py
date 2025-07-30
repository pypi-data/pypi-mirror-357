import urllib
import os
import tarfile
import os.path as path

from spirepy import Study
from spirepy.logger import logger


def download(item: str, target: str, output: str):
    """
    Dowload data from a SPIRE item.

    Arguments:

    item: str
        ID of the target item.
    target: str
        What you want to dowload (MAGs, metadata, genecalls, proteins).
    output: str
        The output folder where the items will be downloaded.
    """
    os.makedirs(output, exist_ok=True)
    if type(item) is Study:
        if target == "metadata":
            item.get_metadata().write_csv(path.join(output, f"{item.name}.csv"))
        elif target == "mags":
            item.download_mags(output)
        else:
            logger.error("No matching item for Study type")
    else:
        if target == "metadata":
            item.get_metadata().write_csv(path.join(output, f"{item.id}.csv"))
        elif target == "mags":
            item.download_mags(output)
        else:
            logger.error("No matching item")
