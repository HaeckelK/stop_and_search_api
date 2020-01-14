"""
Module for fetching data from Police.uk site. Does not include data processing.

API docs: https://data.police.uk/docs/
"""

import requests
import pandas as pd
import time
import os

# TODO Do all my files have the same headers?

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
    def __init__(self):
        return

    def available_old(self):
        """
        Returns
        -------
        df : DataFrame
            date :
            force_list : list of forces
            type : crime data type
        """
        url = URLS['availability']
        response = requests.get(url)
        df = pd.DataFrame(response.json())
        df['type'] = 'stop_and_search'
        df.rename(columns={'stop-and-search': 'force_list'}, inplace=True)
        return df

    def available(self, output_file=None):
        """
        """
        # Default url and basic json to df
        url = URLS['availability']
        df = basic_request_to_df(url)
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

def get_stop_and_search(month, force):
    url = ('https://data.police.uk/api/stops-force?force=' +
           force +
           '&date=' +
           month)
    response = requests.get(url)
    df = pd.DataFrame(response.json())
    df['search_force'] = force
    df['search_month'] = month
    return df

def temp_get_and_save(month, force):
    filename = month + '_' + force + '.csv'
    filename = os.path.join('downloads', filename)
    df = get_stop_and_search(month, force)
    df.to_csv(filename)
    return filename

def temp_download():
    a = get_stop_and_search_availability()

    files = os.listdir('downloads')#existing files

    for index, row in a.iterrows():
        month = row['date']
        forces = row['force_list']

        for force in forces:
            status = ''
            done = ''
            if (month + '_' + force + '.csv') in files:
                continue
            print(month, force)
            time.sleep(0.3)
            try:
                done = temp_get_and_save(month, force)
                status = 'done'
                print(done)
            except:
                status = 'error'
                done = 'NA'
                print('error - no file saved')
            _temp_add_to_log(month, force, done, status)
            

def _temp_add_to_log(month, force, filename, status):
    file = 'logs\\stop_and_search.csv'
    original = pd.read_csv(file)
    data = {'month': [month],
            'force': [force],
            'filename': [filename],
            'download_status': [status]}
    df = pd.DataFrame(data)
    output = original.append(df,sort=False)
    output.to_csv('logs\\stop_and_search.csv',mode='w',index=False)
    return
    

def temp_read_download_files():
    """
    I started downloading files, but didn't keep a log of which had been run.
    Quick script to extract current state of downloads folder.
    """
    files = os.listdir('downloads')
    data = []
    for file in files:
        date = file[:7]
        force = file[8:][:-4]
        data.append([date,force,file])
        
    df = pd.DataFrame(data, columns=['month','force','filename'])
    df['download_status'] = 'done'
    df.to_csv('logs\\stop_and_search.csv',mode='w',index=False)
    return

def temp_check_headers_same(files, expected):
    """
    For a given set of csv files, check that all have the same headers.
    Compare against given headers.
    """
    data = {'file': [],
            'columns_agreed': [],
            'columns_different': []}
    expected = set(expected)
    for i, file in enumerate(files):
        if i%100 == 0:
            print('Processed', i)
        df = pd.read_csv(file, index_col=0)
        data['file'].append(file)
        data['columns_agreed'].append(set(df.columns) == expected)
        data['columns_different'].append(set(df.columns) - expected)
        #print(df.head())
        #print(set(df.columns))
        #print(expected)
        #print(set(df.columns) - expected)
        #break
    df = pd.DataFrame(data)
    return df

def temp_check_download_files_headers():
    print('Checking downloads folder')
    files = list(map(lambda x: os.path.join('downloads',x),
                     os.listdir('downloads')))
    print('Files :', len(files))
    expected = ['age_range','outcome','involved_person','self_defined_ethnicity',
    'gender','legislation','outcome_linked_to_object_of_search','datetime',
                'removal_of_more_than_outer_clothing','outcome_object',
                'location','operation','officer_defined_ethnicity','type',
                'operation_name','object_of_search','search_force','search_month']
    header_check = temp_check_headers_same(files, expected)
    header_check.to_csv('logs\\temp.csv',mode='w')
    return

def temp_combine_files(files,output_name, quiet=False):
    # TODO Doesn't check that the file to df conversion works.
    # TODO Doesn't check that headers are ok.
    # TODO Were any zero lines?
    lines = []
    temp_name = output_name[:-4] + '_temp.csv'

    if not quiet:
        print('Number of files:', len(files))
        
    df = pd.DataFrame() # Empty frame for appending to
    
    for i, file in enumerate(files):
        temp_df = pd.read_csv(file, index_col=0)
        lines.append(temp_df.shape[0])
        df = df.append(temp_df)
        if not quiet and i%50 == 0:
            print('Combined: ',i)

        #if i%100 == 0 or i == len(files) - 1:
         #   if i == 0:
          #      #Start a new file
           #     df.to_csv(temp_name, mode='w')
            #else:
             #   df.to_csv(temp_name, mode='a')
            #df = pd.DataFrame() # Try to offload some memory

    #df = pd.read_csv(temp_name, index_col=0)
    print('-------------')
    print('Sanity Checks')
    print('Input lines: ',sum(lines))
    print('Output lines: ',df.shape[0])
    print('Agreed', sum(lines) == df.shape[0])

    print('-------------')
    print('Save to file')
    df.to_csv(output_name, mode='w')
    print(output_name)
    return

def combine_downloads_folder():
    folder = 'downloads'
    output_name = 'data\\stop_and_search_raw.csv'
    contents = folder_contents(folder)
    print('Combining files in:', folder)
    temp_combine_files(contents, output_name)
    return


