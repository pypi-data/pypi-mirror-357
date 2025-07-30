import polars as pl
from spirepy import Study, Sample
from spirepy.logger import logger


def view(item: str, target: str):
    """
    View a SPIRE item.

    Arguments:

    item: str
        ID of the item to be viewed.
    target: str
        What you want to view (metadata, antibiotic resistance annotations, manifest)
    """

    if type(item) is Study:
        study_match = {
            "metadata": item.get_metadata(),
            "mags": item.get_mags(),
        }.get(target)
        return [
            print(study_match)
            if study_match is not None
            else logger.error("No matching item for Study type")
        ]
    else:
        study_match = {
            "metadata": item.get_metadata(),
            "mags": item.get_mags(),
            "eggnog": item.get_eggnog_data(),
            "amr": item.get_amr_annotations(),
        }.get(target)
        return [
            print(study_match)
            if study_match is not None
            else logger.error("No matching item")
        ]
