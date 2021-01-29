# Orbital Congestion Dashboard
# Written by Nicholas Miller

import pandas as pd
import numpy as np
from datetime import datetime

from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
from skyfield.api import utc


class utils():
    '''
    Various tools used by the Orbital Congestion dashboard
    '''

    intercept_df = None
    sat_df = None
    timescale = None

    def __init__(self, intercept_df=None, sat_df=None):
        '''
        Initialize
        '''
        load = Loader('./data')
        data = load('de421.bsp')
        self.timescale = load.timescale()
        self.intercept_df = intercept_df
        self.sat_df = sat_df

    def generate_satellite_description(self, row=None, sat=None, gp_row=None):
        '''
        Generates the satellite descriptions that are displayed in Cesium
        '''

        if row is not None:
            name = row[sat + '_name'][:-4]
            norad = row[sat + '_norad']
            category = row[sat + '_cat']
            tle = row[sat + '_tle'].replace(',','<br>')
            gp = self.sat_df[self.sat_df['NORAD_CAT_ID'] == norad]

            if len(gp)==1:
                alt_id = gp.iloc[0]['OBJECT_ID']
                obj_typ = gp.iloc[0]['OBJECT_TYPE']
                obj_size = gp.iloc[0]['RCS_SIZE_NAME']
                country = gp.iloc[0]['COUNTRY_CODE']
                launch_dt = gp.iloc[0]['LAUNCH_DATE'].strftime('%Y-%m-%d')
                launch_site = gp.iloc[0]['SITE']
                gp_id = gp.iloc[0]['GP_ID']
        elif gp_row is not None:
            norad = gp_row['NORAD_CAT_ID']
            name = gp_row['OBJECT_NAME']
            category = '---'
            tle = gp_row['TLE_LINE1'] + '<br>' + gp_row['TLE_LINE2']

            alt_id = gp_row['OBJECT_ID']
            obj_typ = gp_row['OBJECT_TYPE']
            obj_size = gp_row['RCS_SIZE_NAME']
            country = gp_row['COUNTRY_CODE']
            if pd.isnull(gp_row['LAUNCH_DATE']):
                launch_dt = 'Unknown'
            else:
                launch_dt = gp_row['LAUNCH_DATE'].strftime('%Y-%m-%d')
            launch_site = gp_row['SITE']
            gp_id = gp_row['GP_ID']


        return f'''
               <p>
               Name: {name} (NORAD ID: {norad})<br>
               Alternate Name: {alt_id}<br>
               SATCAT Operational Status: {category}
               </p>
               <p>
               Type: {obj_typ}<br>
               Size: {obj_size}
               </p>
               <p>
               Country: {country}<br>
               Launch Date: {launch_dt}<br>
               Launch Site: {launch_site}
               </p>
               <p>
               GP ID: {gp_id}<br>
               </p>
               <p>
               TLE:<br>
               {tle}
               </p>
               <p>
               <a href='https://www.n2yo.com/satellite/?s={norad}#results' target='_blank'>More info on N2YO</a>
               </p>
               '''
    def get_xyz(self, row):
        '''
        Gets the x,y,z coordinates of a satellite
        '''
        now  = self.timescale.utc(datetime.utcnow().replace(tzinfo=utc))
        return EarthSatellite(row['TLE_LINE1'], row['TLE_LINE2']).at(now).position.km

    def get_allsat_text(self, x):
        '''
        This sets the text on the satellites when hovering over them
        '''
        text = '<b>Name</b>: ' + str(x['OBJECT_NAME']) + '<br>' +\
               '<b>Country</b>: ' + str(x['country']) + '<br>' +\
               '<b>Object Type</b>: ' + str(x['OBJECT_TYPE']) + '<br>' +\
               '<b>Launch Date</b>: ' + (x['LAUNCH_DATE'].strftime('%Y-%m-%d %H:%M:%S.%f') if pd.notnull(x['LAUNCH_DATE']) else 'Unknown') + '<br>' +\
               '<b>Size</b>: ' + x['RCS_SIZE_NAME'] + '<br>' +\
               '<b>NORAD ID</b>: ' + str(x['NORAD_CAT_ID']) + '<br>' +\
               '<b>Object ID</b>: ' + str(x['OBJECT_ID'])
        return text



    def get_orbit_type(self, row):
        '''
        Categorizies satellites by orbit type
        '''
        if (row['MEAN_MOTION']>11.25) & (row['ECCENTRICITY']<0.25):
            return "LEO"
        elif (row['PERIOD']>=600) & (row['PERIOD']<=800) & (row['ECCENTRICITY']<0.25):
            return "MEO"
        elif (row['MEAN_MOTION']>=0.99) & (row['MEAN_MOTION']<=1.01) & (row['ECCENTRICITY']<0.01):
            return "GEO"
        elif row['ECCENTRICITY'] > 0.25:
            return "HEO"
        else:
            if row['PERIAPSIS'] < 2000:
                return "LEO"
            if (row['PERIAPSIS'] < 35786) & (row['PERIAPSIS'] > 2000):
                return "MEO"
