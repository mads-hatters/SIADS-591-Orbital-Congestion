'''
socrates_gp_history_tle_grab_nm
-------------------------------
This grabs the TLE data from Space-Track for each SOCRATES pair and saves it to a pickle file
https://celestrak.com/SOCRATES/
https://www.space-track.org/

SOCRATES - Satellite Orbital Conjunction Reports Assessing Threatening Encounters in Space
SOCRATES uses Satellite Tool Kit's Conjunction Analysis Tools (STK/CAT) and the NORAD SGP4 propagator implemented in STK

Space-Track
API for extracting TLEs for objects in space.

TLE - Two-line element set
A two-line element set (TLE) is a data format encoding a list of orbital elements of an Earth-orbiting object for a given point in time, the epoch.

Author Nicholas Miller
Date   21 Dec 2020
'''

import pandas as pd
from os import listdir, remove
from os.path import isfile, join
import re

import spacetrack.operators as op
from spacetrack import SpaceTrackClient
from datetime import datetime, timedelta

from tqdm import tqdm

from orbital_congestion import socrates

def grab_gp_history_data(socrates_files_path, tle_file_path, spacetrack_key_file='./spacetrack_pwd.key'):
    '''
    Determines which TLE data is missing and grabs it from Space Track

    Parameters:
    -----------
    socrates_files_path : str
        Relative file path of socrates files

    tle_file_path : str
        Relative file path of TLE data

    spacetrack_key_file : str
        Relative file path of login credentials for spacetrack.
        File format: email,password
    
    Returns
    -------
    None
    '''

    print('Building socrates dataframe...')
    soc_df, tle_df = socrates.get_all_socrates_and_tle_data(socrates_files_path, tle_file_path)
    print('Complete')

    # Get space track login data
    spacetrack_usr, spacetrack_pwd = open(spacetrack_key_file).read()[:-1].split(',')
    st = SpaceTrackClient(identity=spacetrack_usr, password=spacetrack_pwd)

    tmp_tle_file = './tle2.csv'

    # Create a new df of the socrates entries with missing TLE data
    mtle_df1 = tle_df[tle_df['sat1_tle'].isnull()][['sat1_norad','sat1_last_epoch']].rename(columns={'sat1_norad':'norad','sat1_last_epoch':'last_epoch'})
    mtle_df2 = tle_df[tle_df['sat2_tle'].isnull()][['sat2_norad','sat2_last_epoch']].rename(columns={'sat2_norad':'norad','sat2_last_epoch':'last_epoch'})
    miss_tle_df = pd.concat([mtle_df1, mtle_df2])
    miss_tle_df = miss_tle_df.sort_values('last_epoch')

    # Split the missing TLE dataset into bins
    bin_size = 100
    num_bins = round(len(miss_tle_df) / bin_size + 0.49999)
    miss_tle_df['bin'] = pd.qcut(miss_tle_df['last_epoch'], num_bins, labels=list(range(num_bins)))
    print(f'There are {len(miss_tle_df)} missing TLE entries.  We will make {num_bins} requests for this data.')
    print('Getting missing TLE data from Space Track...')

    # For each bin - make a request to SpaceTrack for all norads within that bin with a min/max daterange
    # This will save the data to a CSV file we will parse next (we save to ensure an interrupted progress
    # does not result in a massive amount of lost data)
    count = 0
    for b in tqdm(range(num_bins)):
        tmp_df = miss_tle_df[miss_tle_df['bin'] == b]
        min_epoch = tmp_df['last_epoch'].min().to_pydatetime()
        max_epoch = tmp_df['last_epoch'].max().to_pydatetime()
        epoch_range = op.inclusive_range(min_epoch - timedelta(minutes=5), max_epoch + timedelta(minutes=5))
        all_norads = list(tmp_df['norad'].unique())
        all_data = st.gp_history(norad_cat_id = all_norads, epoch=epoch_range)

        # Write the data to a file
        for idx, row in tmp_df.iterrows():
            d = list(filter(lambda rec: (rec['NORAD_CAT_ID']==str(row['norad'])) & (abs(pd.to_datetime(rec['EPOCH'], format='%Y-%m-%dT%H:%M:%S.%f') - row['last_epoch']) < pd.Timedelta('5 min')), all_data))[0]
            with open(tmp_tle_file, 'a') as f:
                    s = ','.join([str(row['norad']), row['last_epoch'].strftime('%Y%m%d%H%M%S%f'), d['TLE_LINE1'], d['TLE_LINE2'], d['EPOCH']]) 
                    f.write(s + '\n')

    # Open the file created above which contains our new TLE data from SpaceTrack
    new_tle_df = pd.read_csv(tmp_tle_file, names = ['norad','last_epoch', 'tle_line1', 'tle_line2', 'tle_epoch'])
    new_tle_df['last_epoch'] = pd.to_datetime(new_tle_df['last_epoch'], format='%Y%m%d%H%M%S%f')
    print(f'Space Track grabs are complete.')

    # For each TLE record, find the corresponding socrates data and update their TLE
    print(f'Merging {len(new_tle_df)} records with our socrates data...')
    count = 0
    all_success = True
    for index, row in tqdm(new_tle_df.iterrows()):
        found = False
        target = tle_df[(tle_df['sat1_norad'] == row['norad']) & (abs(tle_df['sat1_last_epoch']-row['last_epoch']) < pd.Timedelta('5 min'))].index
        if len(target) > 0:
            found = True
            tle_df.at[target,'sat1_tle'] = row['tle_line1'] + ',' + row['tle_line2']
            tle_df.at[target,'sat1_tle_epoch'] = row['tle_epoch']
            count += 1
        target = tle_df[(tle_df['sat2_norad'] == row['norad']) & (abs(tle_df['sat2_last_epoch']-row['last_epoch']) < pd.Timedelta('5 min'))].index
        if len(target) > 0:
            found = True
            tle_df.at[target,'sat2_tle'] = row['tle_line1'] + ',' + row['tle_line2']
            tle_df.at[target,'sat2_tle_epoch'] = row['tle_epoch']
            count += 1
        if not found:
            print(f'Cant find norad={row["norad"]} for date {row["last_epoch"]} - perhaps we have an updated socrates file?')
            all_success = False
    print(f'Finished merging {count} records')

    # Save the TLE data to a pickle file
    print(f'Saving results...')
    tle_df[['sat_pair','tca_time','sat1_norad','sat2_norad','sat1_tle','sat1_tle_epoch','sat2_tle','sat2_tle_epoch']].to_pickle(tle_file_path, 'gzip')
    print(f'Save to {tle_file_path} complete')

    if all_success:
        remove(tmp_tle_file)
        print(f'Removed temporary file')
    else:
        print('******************************* WARNING *******************************')
        print(f'Please check messages and remove {tmp_tle_file} if everything was okay.')

    return None


socrates_files_path = '../../../data/socrates/'
tle_file_path = '../../../data/socrates_tca_gp_history_tle.pkl.gz'

grab_gp_history_data(socrates_files_path, tle_file_path)
