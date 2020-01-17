"""
Module for fetching data from Police.uk site. Does not include data processing.

API docs: https://data.police.uk/docs/
"""

import requests
import pandas as pd
import time
import os
import itertools

URLS = {'availability': 'https://data.police.uk/api/crimes-street-dates'}


def literal_to_list(x):
    y = x.strip('[]').replace('"', '')
    y = y.replace(' ', '').replace("'", "").split(',')
    return y


class PoliceAPI():
    """
    """
    def __init__(self, delay=1, job_batch=10, savefolder=''):
        self.available = self.get_available()
        self.jobs = pd.DataFrame(columns=['date', 'force', 'status',
                                          'valid_force', 'valid_date'])
        self.default_savefolder = savefolder
        self.default_delay = self._clean_input_int(delay, 1)
        self.default_job_batch = self._clean_input_int(job_batch, 10)
        return

    def get_available(self, output_file=None):
        """
        Stop and Search Data are not available for all forces for all months.

        Returns a dataframe showing force and date (month) for which data
        are available.

        NB: This function is fun when class instantiated and stored in
        self.available.

        Parameters
        ----------
        output_file : str
            Full file path + extension of file to save dataframe.
            (Default : None, no file will be saved)

        Returns
        -------
        df : dataframe
            dataframe containing 'force', 'date', and 'type'.
        """
        # Default url and basic json to df
        url = self.url_available()
        df = self._basic_request_to_df(url)

        # Bad response will return None
        if df is None:
            print('No data found from', url)
            print('Availability data cannot be checked')
            print('This may result in bad requests sent to API')
            return df

        # Tidy up headers
        df.rename(columns={'stop-and-search': 'force_list'}, inplace=True)
        # Reformat to show one force per line
        df = self._extract_forces(df)
        # Note that these are stop_and_search
        df['type'] = 'stop_and_search'
        if output_file is not None:
            if os.path.basename(output_file).isspace():
                output_file = os.path.join(os.path.dirname(output_file),
                                           'available.csv')
                print('output_file had no filename. Replaced with ',
                      output_file)
            # TODO : output_file a path? is it csv?
            df.to_csv(output_file, index=False)
        return df

    def url_available(self):
        return URLS['availability']

    def _extract_forces(self, df):
        # Forces are in list format - extract into one force per line
        new_df = pd.DataFrame(columns=['force', 'date'])
        for index, row in df.iterrows():
            date = row['date']
            forces = row['force_list']
            try:
                temp_df = pd.DataFrame(forces, columns=['force'])
            except ValueError:
                forces = literal_to_list(forces)
                temp_df = pd.DataFrame(forces, columns=['force'])
            temp_df['date'] = date
            new_df = new_df.append(temp_df, sort=False)
        return new_df

    def download(self, delay=None, save=True):
        """
        """
        if delay is None:
            delay = self.default_delay
        delay = self._clean_input_int(delay, self.default_delay)
        savefolder = self.default_savefolder
        # Create folder if it does not exist
        if os.path.exists(savefolder) is False:
            os.mkdir(savefolder)
            print('\nCreated Folder {}\n'.format(savefolder))

        df = self.jobs.copy()
        for index, row in df.iterrows():
            date, force = row['date'], row['force']
            print(date, force, end="")
            time.sleep(delay)
            filename = self._download(date, force, savefolder)
            print(filename)
        return

    def _download(self, date, force, savefolder):
        filename = self._temp_get_and_save(date, force, savefolder)
        return filename

    def add_job(self, dates=None, forces=None):
        new_jobs = pd.DataFrame(columns=['date', 'force'])

        if dates is None and forces is None:
            print('Note: No dates of forces have been entered')
            print('By default this will add all available records')
            print('to download jobs.')

        if dates is None or forces is None:
            if self.available is None:
                # IF self.available had a 404 it will be None
                print('self.available is None no list can be used to')
                print('auto insert dates / forces.')
                return

        if dates is None:
            dates = list(self.available['date'].unique())

        if forces is None:
            forces = list(self.available['force'].unique())

        # dates and forces must be list or None
        input_type_ok = self._check_dates_forces_input_type(dates, forces)

        if input_type_ok is False:
            print('forces and dates must be a list type')
            print('Job not added')
            return

        dates = self._remove_non_str(dates)
        forces = self._remove_non_str(forces)
        if not dates or not forces:
            print('Input list is now empty no items added to job.')
            return

        if isinstance(dates, list) and isinstance(forces, list):
            # Convert forces to lowercase
            forces = list(map(str.lower, forces))
            pairs = set(itertools.product(dates, forces))
            new_jobs = pd.DataFrame(pairs, columns=['date', 'force'])

        # Check that date and force are valid
        new_jobs['valid_date'] = new_jobs['date'].apply(lambda x: self._valid_date(x))
        new_jobs['valid_force'] = new_jobs['force'].apply(lambda x: self._valid_force(x))

        new_jobs['status'] = 'not_done'

        # Add to central jobs list
        self.jobs = self.jobs.append(new_jobs,
                                     sort=False)

        # Information to user
        print('\nJob added')
        print('Dates', dates)
        print('Forces', forces)
        print('Request Count:', len(new_jobs))
        return

    def _valid_date(self, date):
        return date in self.dates

    def _valid_force(self, force):
        return force in self.forces

    def _valid(self):
        return

    def _temp_get_and_save(self, month, force, savefolder):
        filename = month + '_' + force + '.csv'
        filename = os.path.join(savefolder, filename)
        df = self._get_stop_and_search(month, force)
        df.to_csv(filename)
        return filename

    def _get_stop_and_search(self, month, force):
        url = ('https://data.police.uk/api/stops-force?force=' +
               force +
               '&date=' +
               month)
        response = requests.get(url)
        df = pd.DataFrame(response.json())
        df['search_force'] = force
        df['search_month'] = month
        return df

    @property
    def forces(self):
        return self._from_available('force')

    @property
    def dates(self):
        return self._from_available('date')

    def _from_available(self, field):
        # return column of available as list
        # ensure available is not None
        if self.available is not None:
            return list(self.available[field].unique())
        else:
            return []

    def _clean_input_int(self, value, replacement=None):
        # Convert input to int if not possible replace with
        # replacement value
        try:
            x = int(value)
        except (ValueError, TypeError):
            x = replacement
        if x <= 0:
            x = replacement
        return x

    def _basic_request_to_df(self, url):
        # TODO : response handling
        response = self._get_response(url)
        if response.status_code == 200:
            print('200 response from', url)
            df = pd.DataFrame(response.json())
            return df
        if response.status_code == 404:
            print('404 response from', url)
            return

    def _get_response(self, url):
        # Added this function for allow mocking of response in testing
        return requests.get(url)

    def _check_dates_forces_input_type(self, dates, forces):
        # If at least one of them is not a list return false
        x = sum([True for c in (dates, forces) if not isinstance(c, list)])
        return x == 0

    def _remove_non_str(self, mylist):
        remove = [f for f in mylist if not isinstance(f, str)]
        if remove:
            print('Input forces / dates must be string type.')
            print('The following have been removed and not added to job.')
            print(remove)
        remaining = [f for f in mylist if f not in remove]

        return remaining
