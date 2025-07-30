from .fixtures import study


def test_len_samples(study):
    assert len(study.get_samples()) == 3


def test_name(study):
    assert study.name == "Minot_2013_gut_phage"
