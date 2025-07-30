import pytest

from spirepy import Study


@pytest.fixture
def study():
    "A simple study from the SPIRE database"
    return Study(name="Minot_2013_gut_phage")
