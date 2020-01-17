import pytest
import pandas as pd
import pandas.util.testing as tm

from context import police_stop_and_search_api
from police_stop_and_search_api.police_api import PoliceAPI


fixtures = {'available_clean': 'fixtures\\available.csv',
            'available_raw': 'fixtures\\available_raw.csv'}


class MockResponse():
    def __init__(self):
        self.status_code = None
        self.url = None
        self.headers = None


def mock_get_response(self, url):
    mr = MockResponse()
    mr.url = url
    mr.status_code = 404
    print(url)
    return mr


# PoliceAPI init calls get_available, which makes a request to an external
# url
def monkeypatch_get_available(*args, **kwargs):
    print('Monkey patch get_available has been called')
    return


def mock_request_to_df(*args, **kwargs):
    print('mock request to df has been called')
    df = pd.read_csv(fixtures['available_raw'])
    return df


def test_init(monkeypatch):
    """
    Test that class attributes correctly applied.
    """
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()
    print(police.available)
    assert police.default_delay == 1
    assert police.default_job_batch == 10
    assert police.default_savefolder == ''


@pytest.mark.parametrize("delay,expected", [
    (2, 2),
    (10, 10),
    (-1, 1),
    ('string', 1),
    (3.14, 3),
    (str, 1)
])
def test_init_delay(monkeypatch, delay, expected):
    """
    Test that class attributes correctly applied.
    """
    monkeypatch.setattr(PoliceAPI, "get_available", monkeypatch_get_available)
    police = PoliceAPI(delay=delay)
    assert police.default_delay == expected


@pytest.mark.parametrize("job_batch,expected", [
    (2, 2),
    (10, 10),
    (-1, 10),
    ('string', 10),
    (3.14, 3)
])
def test_init_job_batch(monkeypatch, job_batch, expected):
    """
    Test that class attributes correctly applied.
    """
    monkeypatch.setattr(PoliceAPI, "get_available", monkeypatch_get_available)
    police = PoliceAPI(job_batch=job_batch)
    assert police.default_job_batch == expected


def test_get_available(monkeypatch):
    """
    Test that raw data cleaned as expected
    """
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()
    result_df = police.get_available()
    expected_df = pd.read_csv(fixtures['available_clean'])
    assert tm.assert_frame_equal(result_df.reset_index(drop=True),
                                 expected_df.reset_index(drop=True)) is None


def test_available(monkeypatch):
    """
    Check that self.available has been processed.
    """
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()
    result_df = police.available
    expected_df = police.get_available()
    assert tm.assert_frame_equal(result_df.reset_index(drop=True),
                                 expected_df.reset_index(drop=True)) is None


@pytest.mark.parametrize("filename", [
    'available_clean.csv',
    'available_clean'
])
def test_get_available_save(monkeypatch, tmpdir, filename):
    """
    """
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()
    file = tmpdir.join(filename)
    police.get_available(output_file=str(file))
    result_df = pd.read_csv(file)
    expected_df = pd.read_csv(fixtures['available_clean'])
    assert tm.assert_frame_equal(result_df.reset_index(drop=True),
                                 expected_df.reset_index(drop=True)) is None


def test_get_available_status_404(monkeypatch):
    monkeypatch.setattr(PoliceAPI, "_get_response", mock_get_response)
    police = PoliceAPI()
    assert police.available is None
