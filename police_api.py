"""
Module for fetching data from Police.uk site. Does not include data processing.

API docs: https://data.police.uk/docs/
"""

import requests
import pandas as pd
import time
import os
import itertools

URLS = {'availability' : 'https://data.police.uk/api/crimes-street-dates'}

def basic_request_to_df(url):
    # TODO : response handling
    response = requests.get(url)
    df = pd.DataFrame(response.json())
    return df

def literal_to_list(x):
    y = x.strip('[]').replace('"', '').replace(' ', '').replace("'", "").split(',')
    return y

class police_api():
    """
    """
    def __init__(self, delay=1, job_batch=10, savefolder=''):
        self.available = self.get_available()
        self.jobs = pd.DataFrame(columns=['date', 'force', 'status'])
        self.default_savefolder = savefolder
        self.default_delay = delay
        self.default_job_batch = job_batch
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
        url = URLS['availability']
        df = basic_request_to_df(url)
        #df.to_csv('testing\\available_raw.csv', index=False)
        #df = pd.read_csv('testing\\available_raw.csv')
        # Tidy up headers
        df.rename(columns={'stop-and-search': 'force_list'}, inplace=True)
        # Reformat to show one force per line
        df = self._extract_forces(df)
        # Note that these are stop_and_search
        df['type'] = 'stop_and_search'
        if output_file is not None:
            df.to_csv(output_file, index=False)
        return df

    def _extract_forces(self, df):
        # Forces are in list format - extract into one force per line
        new_df = pd.DataFrame(columns=['force', 'date'])
        for index, row in df.iterrows():
            date = row['date']
            forces = row['force_list']
            #forces = literal_to_list(forces)
            temp_df = pd.DataFrame(forces, columns=['force'])
            temp_df['date'] = date
            new_df = new_df.append(temp_df, sort=False)
        return new_df

    def download(self, delay=None):
        if delay is None:
            delay = self.default_delay
        savefolder = self.default_savefolder
        df = self.jobs.copy()
        for index, row in df.iterrows():
            date, force = row['date'], row['force']
            print(date, force)
            time.sleep(delay)
            self._download(date, force, savefolder)
        return

    def _download(self, date, force, savefolder):
        filename = self._temp_get_and_save(date, force, savefolder)
        return

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
        new_jobs['valid_force'] = new_jobs['force'].apply(lambda x: self._valid_date(x))                

        new_jobs['status'] = 'not_done'

        # Add to central jobs list
        self.jobs = self.jobs.append(new_jobs,
                                     sort=False)
        return

    def _valid_date(self, date):
        return date in self.available['date'].unique()

    def _valid_force(self, force):
        return force in self.available['force'].unique()

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
