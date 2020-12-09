'''
socrates_scrapper_nm
--------------------
Scrapes the SOCRATES website for upcoming satellite collision data.
https://celestrak.com/SOCRATES/

SOCRATES - Satellite Orbital Conjunction Reports Assessing Threatening Encounters in Space
SOCRATES uses Satellite Tool Kit's Conjunction Analysis Tools (STK/CAT) and the NORAD SGP4 propagator implemented in STK

Author Nicholas Miller
Date   9 Dec 2020
'''

import pandas as pd
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from os import listdir
from os.path import isfile, join
import re

def get_last_save_date(path):
    '''
    Get the date on the most recent file
    
    Parameters:
    -----------
    path : str
        Relative file path
    
    Returns
    -------
    file : str
        The most recent filename
        
    date : datetime
        Contains the most recent date
    '''
    
    files = [ (match[0],match[1]) for f in listdir(path) if isfile(join(path, f))  if (match:=re.search('^socrates_([0-9]{14})\.csv(\.gz)?$', f))]
    try:
        file,date = sorted(files, reverse=True)[0]
        return file, datetime.strptime(date, '%Y%m%d%H%M%S')
    except:
        return '', datetime.min

def scrape_socrates(num_of_records, min_hours, data_file_path, sort_list):
    '''
    Scrape the SOCRATES website for upcoming close flybys
    
    Parameters:
    -----------
    num_of_records : int
        Number of records to request from SOCRATES
    
    min_hours : int
        Minimum number of hours betwen file saves
        
    data_file_path: str
        Relative file path
    
    sort_list : list(str)
        Each sort order to download
    '''

    cidx_map = {1: 'sat1_norad', 2: 'sat1_name', 3: 'sat1_days_epoch', 4: 'max_prob', 5: 'dil_thr_km', 6: 'min_rng_km',
                7: 'rel_velo_kms', 8: 'sat2_norad', 9: 'sat2_name', 10: 'sat2_days_epoch', 11: 'start_time',
                12: 'tca_time', 13: 'stop_time'}

    # Save the datetime this was scraped
    extract_date = datetime.utcnow()
    concat_df = pd.DataFrame()
    print (f'{extract_date} UTC - Job started')
    
    for sort in sort_list:
        # Scrape data
        print(f'Making {sort} web request...')
        url = 'https://celestrak.com/SOCRATES/search-results.php?IDENT=NAME&NAME_TEXT1=&NAME_TEXT2=&CATNR_TEXT1=&CATNR_TEXT2=&ORDER=' + sort + '&MAX=' + str(num_of_records) + '&B1=Submit'
        response = requests.get(url)
        print('Request complete.  Begin Parsing...')


        # Parse Data
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all('table')[3]
        rows = []

        for record in table.find_all('form'):
            row = {}
            for idx, cell in enumerate(record.find_all('td')):
                if idx in cidx_map.keys():
                    row[cidx_map[idx]] = cell.text
            rows.append(row)
        print('Parsing complete.')

        # Convert the data into a Pandas Dataframe
        df = pd.DataFrame(rows)
        df['extract_sort'] = sort
        df['extract_date'] = extract_date
        concat_df = concat_df.append(df)

    # Save the file if none newer than the min_hours exists
    recent_file, recent_date = get_last_save_date(data_file_path)
    time_dif = extract_date - recent_date
    if time_dif > timedelta(hours=min_hours):
        filename = 'socrates_' + extract_date.strftime('%Y%m%d%H%M%S') + '.csv.gz'
        concat_df.to_csv(data_file_path + filename, index=False)
        print(f'Saving of file \'{filename}\' complete.  Please be sure to commit new file!')
    else:
        print(f'Not saving file since a file was created {time_dif} ago: {recent_file}')

    print (f'{datetime.utcnow()} UTC - Job ended')
    return concat_df
    

# Parameters:
#-----------------
num_of_records = 1000
min_hours = 6
data_file_path = '../../../data/socrates/'
sort = ['MAXPROB', 'MINRANGE', 'TIMEIN']

scrape_socrates (num_of_records, min_hours, data_file_path, sort)
