# Orbital Congestion Dashboard
# Written by Nicholas Miller

import pandas as pd

import oc_dash_utils

try:
    # Package not included with Heroku
    import sys
    sys.path.append('..')
    from pkg.orbital_congestion import socrates
except:
    pass



def load_intercept_data():
    '''
    Loads the pandas dataframe for intercepts
    '''
    socrates_files_path = '../data/socrates/'
    tle_file_path = '../data/socrates_tca_gp_history_tle.pkl.gz'

    soc_df, tle_df = socrates.get_all_socrates_and_tle_data(socrates_files_path, tle_file_path)
    tle_df = socrates.assign_socrates_category(tle_df, True)
    tle_df = tle_df[tle_df['rel_velo_kms'] > 0.01].sort_values(by='max_prob', ascending=False)

    return tle_df

def load_satellite_data():
    '''
    Loads the pandas dataframe for current satellite tracking
    '''
    u = oc_dash_utils.utils()
    gpd_df = pd.read_csv("../data/space-track-gp/gp_20201214.csv.gz")
    sat_df = pd.read_pickle("../data/satcat_incl_breakup_dates.pkl.gz")

    columns = [c for c in gpd_df.columns]

    gpd_df['LAUNCH_DATE'] = pd.to_datetime(gpd_df['LAUNCH_DATE'], format='%Y-%m-%d')
    gpd_df['DECAY_DATE'] = pd.to_datetime(gpd_df['DECAY_DATE'], format='%Y-%m-%d')

    gpd_df = pd.merge(gpd_df, sat_df, how='left', on='NORAD_CAT_ID')

    gpd_df['LAUNCH_DATE'] = gpd_df.apply(lambda x: x['LAUNCH_DATE'] if x['exist_date'] is None else x['exist_date'], axis=1)
    gpd_df = gpd_df.rename(columns={'OBJECT_TYPE_y': 'OBJECT_TYPE'})
    
    gpd_df['RCS_SIZE'] = gpd_df['RCS_SIZE'].fillna('X')
    
    gpd_df['description'] = gpd_df.apply(lambda x: u.generate_satellite_description(gp_row=x), axis=1)
    columns.append('description')

    return gpd_df[columns]

def load_data():
    '''
    Faster load if other saved pickle files from other load functions
    '''
    satellite_data = pd.read_pickle("./data/satellite_data.pkl.gz")
    intercept_data = pd.read_pickle("./data/intercept_data.pkl.gz")
    return satellite_data, intercept_data
