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


def mock_response_404(self, url):
    mr = MockResponse()
    mr.url = url
    mr.status_code = 404
    print('mock_response_404 called', url)
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
    monkeypatch.setattr(PoliceAPI, "_get_response", mock_response_404)
    police = PoliceAPI()
    assert police.available is None


@pytest.mark.parametrize('dates, forces, job_len', [
    (None, None, 1584),
    (float, None, 0),
    (None, float, 0),
    (float, float, 0),
    (int, str, 0),
    (['2019-10', '2019-07'], ['cambridgeshire', 'cheshire'], 4),
    (['2019-10'], ['cambridgeshire', 'cheshire'], 2),
    (['2019-08', '2019-07'], None, 88),
    (['2019-08', '2019-07'], ['cheshire'], 2)
])
def test_add_job_input_type_major(monkeypatch, dates, forces, job_len):
    """
    Check that only input lists are accepted. Checked by counting jobs
    added to police.jobs dataframe.
    """
    # This will give police.available from fixtures
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()

    police.add_job(dates=dates, forces=forces)
    df = police.jobs
    assert len(df) == job_len


@pytest.mark.parametrize('dates, forces, job_len', [
    (['2019-08', '2019-07'], ['cheshire'], 2),
    (['2019-08', '2019-07'], [float, 'cheshire'], 2),
    (['2019-08', '2019-07'], [int], 0),
    (['2019-08', int], ['cheshire'], 1),
    ([float, '2019-07'], ['cheshire'], 1),
    ([int], ['cheshire'], 0),
])
def test_add_job_input_type_minor(monkeypatch, dates, forces, job_len):
    """
    Check that only input strings are accepted for forces / dates.
    Checked by counting jobs added to police.jobs dataframe.
    """
    # This will give police.available from fixtures
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()

    police.add_job(dates=dates, forces=forces)
    df = police.jobs
    assert len(df) == job_len


@pytest.mark.parametrize('dates, forces, job_len', [
    (['2019-08', '2019-07'], ['cheshire'], 2),
    (['2019-08', '2019-07'], ['cheSHire'], 2),
    (['2019-08', '2019-07'], ['CHESHIRE'], 2),
])
def test_add_job_force_case(monkeypatch, dates, forces, job_len):
    """
    Check that function is insensitive to force case.
    Checked by counting True in valid_force
    """
    # This will give police.available from fixtures
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()

    police.add_job(dates=dates, forces=forces)
    df = police.jobs
    assert len(df[df['valid_force'] == True]) == job_len


@pytest.mark.parametrize('dates, forces, force_count, date_count', [
    (['2019-08', '2019-07'], ['cheshire'], 2, 2),
    (['2019-08', '2019-07'], None, 88, 88),
    (['2019-08', '2019-07'], ['X', 'cheshire'], 2, 4),
    (['2019-08', '2019-07'], ['X'], 0, 2),
    (['2019-08', '2019-X7'], ['cheshire'], 2, 1),
    (['2019-Z7'], ['X'], 0, 0),
    (None, None, 1584, 1584),
])
def test_add_job_valid(monkeypatch, dates, forces, force_count, date_count):
    """
    Check that add_job correctly chooses valid for valid_force, valid_date.
    Checked by counting True in valid_force and valid_count
    """
    # This will give police.available from fixtures
    monkeypatch.setattr(PoliceAPI, "_basic_request_to_df", mock_request_to_df)
    police = PoliceAPI()

    police.add_job(dates=dates, forces=forces)
    df = police.jobs
    assert len(df[df['valid_force'] == True]) == force_count
    assert len(df[df['valid_date'] == True]) == date_count


@pytest.mark.parametrize('dates, forces, job_len', [
    (['2019-08', '2019-07'], ['cheshire'], 2),
    (['2019-08', '2019-07'], None, 0),
    (['2019-08', '2019-07'], ['X', 'cheshire'], 4),
    (['2019-08', '2019-07'], ['X'], 2),
    (['2019-08', '2019-X7'], ['cheshire'], 2),
    (['2019-Z7'], ['X'], 1),
    (None, None, 0),
])
def test_add_job_valid_404(monkeypatch, dates, forces, job_len):
    """
    Check that add_job marks valid_force / date as False if available
    is not returned due to 404.
    Checked by counting True in valid_force and valid_date and job_len
    """
    # This will give police.available is None
    monkeypatch.setattr(PoliceAPI, "_get_response", mock_response_404)
    police = PoliceAPI()

    police.add_job(dates=dates, forces=forces)
    df = police.jobs
    assert len(df[df['valid_force'] == True]) == 0
    assert len(df[df['valid_date'] == True]) == 0
    assert len(df) == job_len
# test_add_job_available_none
