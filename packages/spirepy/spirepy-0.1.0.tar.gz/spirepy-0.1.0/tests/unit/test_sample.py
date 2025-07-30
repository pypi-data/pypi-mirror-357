from .fixtures import study


def test_sample_name(study):
    sample = study.get_samples()[0]
    assert sample.id == "SAMN02044683"
