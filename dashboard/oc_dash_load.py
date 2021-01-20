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
    tle_file_path = '../data/space-track-gp-history/gp_history_socrates_tca_tles.pkl.gz'

    soc_df, tle_df = socrates.get_all_socrates_and_tle_data(socrates_files_path, tle_file_path)
    tle_df = socrates.assign_socrates_category(tle_df, True)
    tle_df = tle_df[tle_df['rel_velo_kms'] > 0.01].sort_values(by='max_prob', ascending=False)

    return tle_df

def load_satellite_data():
    '''
    Loads the pandas dataframe for current satellite tracking
    '''
    u = oc_dash_utils.utils()
    gpd_df = pd.read_csv("../data/space-track-gp/gp_20210119.csv.gz")
    sat_df = pd.read_pickle("../data/satcat_incl_breakup_dates.pkl.gz")

    columns = [c for c in gpd_df.columns]

    gpd_df['LAUNCH_DATE'] = pd.to_datetime(gpd_df['LAUNCH_DATE'], format='%Y-%m-%d')
    gpd_df['DECAY_DATE'] = pd.to_datetime(gpd_df['DECAY_DATE'], format='%Y-%m-%d')

    gpd_df = pd.merge(gpd_df, sat_df, how='left', on='NORAD_CAT_ID')

    gpd_df['LAUNCH_DATE'] = gpd_df.apply(lambda x: x['LAUNCH_DATE'] if x['exist_date'] is None else x['exist_date'], axis=1)
    gpd_df = gpd_df.rename(columns={'OBJECT_TYPE_y': 'OBJECT_TYPE'})
    
    # Set x,y,z coordinates
    gpd_df[['x','y','z']] = gpd_df.apply(u.get_xyz,axis=1).to_list()
    columns.extend(['x','y','z'])

    # Extend RCS_SIZE description
    rcs_map = {'SMALL':'Small (< 0.1m^2)', 'MEDIUM':'Medium (0.1m^2 - 1m^2)','LARGE': 'Large (>1m^2)', 'X': 'Unknown'}
    gpd_df['RCS_SIZE_NAME'] = gpd_df['RCS_SIZE'].fillna('X').map(rcs_map)
    columns.append('RCS_SIZE_NAME')
    
    # Cesium Satellite descriptions
    gpd_df['description'] = gpd_df.apply(lambda x: u.generate_satellite_description(gp_row=x), axis=1)
    columns.append('description')

    # Setup marker size based on RCS_SIZE
    size_map = {'SMALL':3, 'MEDIUM':4, 'LARGE':5}
    gpd_df['allsat_marker_size'] = gpd_df['RCS_SIZE'].fillna('MEDIUM').map(size_map)
    columns.append('allsat_marker_size')
        
    # Use full country (company) names
    ctry_map = {'PRC':'China', 'US':'USA', 'CIS':'Former USSR', 'UAE':'United Arab Emirates', 'JPN':'Japan', 'FR':'France',
                'ESA':'European Space Agency', 'NZ':'New Zealand', 'TBD':'Unknown', 'CA':'Canada', 'IND':'India',
                'LTU':'Lithuania', 'ARGN':'Argentina', 'GER':'Germany', 'FIN':'Finland', 'THAI':'Thailand', 'EST':'Estonia',
                'AUS':'Australia', 'SPN':'Spain', 'ISRA':'Israel', 'BEL':'Belgium', 'SVN':'Slovenia', 'IT':'Italy',
                'SKOR':'South Korea', 'IRAN':'Iran', 'ORB':'Orbcomm', 'ITSO':'ITSO', 'UK':'UK', 'EUTE':'Eutelsat', 
                'CHBZ':'China/Brazil', 'IM':'Inmarsat', 'EGYP':'Egypt', 'RWA':'Rwanda', 'ISS':'International Space Station',
                'SDN':'SDN', 'POL':'Poland', 'MEX':'Mexico', 'ROC':'Taiwan', 'SING':'Singapore', 'LKA':'Sri Lanka',
                'NPL':'Nepal', 'AB':'Arab Sat Comm', 'O3B':'O3B Networks', 'SWTZ':'Switerland', 'INDO':'Indonesia',
                'GREC':'Greece', 'SAFR':'South Africa', 'SAUD':'Saudia Arabia', 'JOR':'Jordan', 'KAZ':'Kazakhstan',
                'NETH':'Netherlands', 'COL':'Columbia', 'MA':'Morocco', 'QAT':'Qatar', 'EUME':'EUMETSAT', 'RP':'Philippines',
                'AZER':'Azerbaijan', 'PAKI':'Pakistan', 'SES':'Societe Europeenee Des Satellites', 'KEN':'Keyna',
                'BGD':'Bangladesh', 'DEN':'Denmark', 'AGO':'Angola', 'ALG':'Alteria', 'VENZ':'Venezuela', 'AC':'AsiaSat',
                'NOR':'Norway', 'BGR':'Bulgaria', 'CZCH':'Czech Republic', 'CHLE':'Chile', 'ASRA':'Austria', 'BRAZ':'Brazil',
                'TURK':'Turkey', 'PER':'Peru', 'BERM':'BERM', 'NKOR':'North Korea', 'BELA':'Belarus', 'LAOS':'Laos',
                'TMMC':'Turkmenistan/Monaco', 'MALA':'Malaysia', 'IRAQ':'Iraq', 'UKR':'Ukraine', 'URY':'Uruguay',
                'SEAL':'Sea Launch', 'FRIT':'France/Italy', 'BOL':'Bolivia', 'ECU':'Ecuador', 'VTNM':'Vietnam',
                'GLOB':'Globalstar', 'NIG':'Nigeria', 'LUXE':'Luxembourg', 'STCT':'Singapore/Taiwan', 'RASC':'RASCOM',
                'SWED':'Sweden', 'USBZ':'US/Brazil', 'NICO':'NEW ICO', 'NATO':'NATO', 'POR':'Portugal', 'FGER':'France/Germany'
                }
    gpd_df['COUNTRY_CODE'] = gpd_df['COUNTRY_CODE'].fillna('TBD')
    gpd_df['country'] = gpd_df['COUNTRY_CODE'].map(ctry_map)
    columns.append('country')
    
    # Set text to appear on allsat satellites
    gpd_df['allsat_text'] = gpd_df.apply(u.get_allsat_text, axis=1)
    columns.append('allsat_text')
    
    return gpd_df[columns]

def load_data():
    '''
    Faster load if other saved pickle files from other load functions
    '''
    satellite_data = pd.read_pickle("./data/satellite_data.pkl.gz")
    intercept_data = pd.read_pickle("./data/intercept_data.pkl.gz")
    return satellite_data, intercept_data
