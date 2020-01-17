"""
Module for fetching data from Police.uk site. Does not include data processing.

API docs: https://data.police.uk/docs/
"""

import requests
import pandas as pd
import time
import os, sys
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
        self.jobs = pd.DataFrame(columns=['date', 'force', 'status'])
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

        if dates is None:
            dates = list(self.available['date'].unique())

        if forces is None:
            forces = list(self.available['force'].unique())

        if isinstance(dates, list) and isinstance(forces, list):
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
        return list(self.available['force'].unique())

    @property
    def dates(self):
        return list(self.available['date'].unique())

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
