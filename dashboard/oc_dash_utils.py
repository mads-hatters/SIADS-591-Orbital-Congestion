# Orbital Congestion Dashboard
# Written by Nicholas Miller

import pandas as pd
import numpy as np



class utils():
    '''
    Various tools used by the Orbital Congestion dashboard
    '''

    intercept_df = None
    sat_df = None

    def __init__(self, intercept_df=None, sat_df=None):
        '''
        Initialize
        '''
        self.intercept_df = intercept_df
        self.sat_df = sat_df

    def generate_satellite_description(self, row=None, sat=None, gp_row=None):
        '''
        Generates the satellite descriptions that are displayed in Cesium
        '''
        rcs_map = {'SMALL':'Small (< 0.1m^2)', 'MEDIUM':'Medium (0.1m^2 - 1m^2)','LARGE': 'Large (>1m^2)', 'X': 'Unknown'}

        if row is not None:
            name = row[sat + '_name'][:-4]
            norad = row[sat + '_norad']
            category = row[sat + '_cat']
            tle = row[sat + '_tle'].replace(',','<br>')
            gp = self.sat_df[self.sat_df['NORAD_CAT_ID'] == norad]

            if len(gp)==1:
                alt_id = gp.iloc[0]['OBJECT_ID']
                obj_typ = gp.iloc[0]['OBJECT_TYPE']
                obj_size = rcs_map[gp.iloc[0]['RCS_SIZE']]
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
            obj_size = rcs_map[gp_row['RCS_SIZE']]
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
