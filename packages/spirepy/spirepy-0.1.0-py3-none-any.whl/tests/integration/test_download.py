from .fixtures import study
import tempfile
import os
from spirepy.cli.spire import maincall


def test_download_mags(study):
    with tempfile.TemporaryDirectory() as tmpdir:
        sample = study.get_samples()[1]
        maincall(sample, "download", "mags", tmpdir)
        assert len(os.listdir(tmpdir)) == 2
