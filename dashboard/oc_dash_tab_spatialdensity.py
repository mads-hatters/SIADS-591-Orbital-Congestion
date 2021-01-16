# Orbital Congestion Dashboard
# Written by Nicholas Miller

import dash
import dash_html_components as html
import dash_core_components as dcc

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import math



class spatial_density():
    '''
    Shows spatial density and related graphics
    '''

    sat_df = None

    def __init__(self, sat_df):
        '''
        Initialize
        '''
        self.sat_df = sat_df

    def __altitude_band_volume(self, outer_radius, inner_radius):
        '''
        Determines the volumn of an altitude band around a sphere
        '''
        return 4/3*np.pi*math.pow(outer_radius,3) - \
               4/3*np.pi*math.pow(inner_radius,3)

    def __generate_spatial_density_by_year(self):
        '''
        Generates an interactive Plotly graphic showing the spatial density
        '''
        earth_radius = 6371
        bin_size = 10
        bins = np.arange(200,2000+bin_size,bin_size)
        built_df = pd.DataFrame()
        start = int(self.sat_df['LAUNCH_DATE'].dt.year.min())
        spd_df = self.sat_df.dropna(subset=['LAUNCH_DATE']).copy()
        spd_df['ALT_BIN'] = pd.cut(spd_df['PERIAPSIS'], bins=bins, labels=bins[:-1])

        for y in np.arange(start,2021):
            tmp_df = spd_df[(spd_df['MEAN_MOTION']>11.25) &
                        (spd_df['ECCENTRICITY']<0.25) &
                        ((spd_df['DECAY_DATE'].isnull()) | (spd_df['DECAY_DATE'].dt.year > y+2)) &
                        (spd_df['LAUNCH_DATE'].dt.year <= y)].groupby('ALT_BIN')['CCSDS_OMM_VERS'].count().reset_index()
            tmp_df.columns = ['ALT','ALL_COUNT']
            tmp_df['YEAR'] = y
            built_df = pd.concat([built_df,tmp_df])

        built_df['ALL_DENSITY'] = built_df.apply(lambda x: x['ALL_COUNT'] / self.__altitude_band_volume(earth_radius+x['ALT']+bin_size, earth_radius+x['ALT']), axis=1)


        fig = px.line(built_df, x="ALT", y="ALL_DENSITY", title='Satellite Density in Low Earth Orbit (LEO) by Altitude',
                      animation_frame="YEAR", range_x=[200,2000], range_y=[0,0.00000013],
                      labels={
                          "ALT": "Altitude (km)",
                          "ALL_DENSITY": "Count/km^3",
                          "YEAR": "Year"
                      })

        # Annotate last frame
        fig.add_annotation(
            x=545,
            y=0.0000001,
            text='Starlink Satellites',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            ax=100,
            ay=0
        )

        # Set last frame as default
        last_frame_num = len(fig.frames) -1
        fig.layout['sliders'][0]['active'] = last_frame_num
        fig = go.Figure(data=fig['frames'][-1]['data'], frames=fig['frames'], layout=fig.layout)

        return fig

    def __generate_satellite_count_by_year(self):
        '''
        Generates an interactive Plotly graphic showing cumulative satellite count
        '''
        df = self.sat_df.dropna(subset=['LAUNCH_DATE']).copy()
        count_df = df[(df['MEAN_MOTION']>11.25) & (df['ECCENTRICITY']<0.25)].groupby(df['LAUNCH_DATE'].dt.year)[['CCSDS_OMM_VERS']].count()
        decay_df = df[(df['MEAN_MOTION']>11.25) & (df['ECCENTRICITY']<0.25)].groupby(df['DECAY_DATE'].dt.year)[['CCSDS_OMM_VERS']].count()
        decay_df = decay_df.append(pd.DataFrame([0], columns=['CCSDS_OMM_VERS'], index=[1958]))
        count_df = (count_df - decay_df).cumsum()
        count_df.columns = ['count']

        fig = px.line(count_df, x=count_df.index, y='count', title='Satellites in LEO by Year',
                      labels={"index": "Year","count": "Number of Satellites"})


        # Add event annotations
        fig.add_trace(go.Scatter(x=[1981.5],y=[5300],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='Space Shuttle enters service in April 1981<extra></extra>'))

        fig.add_trace(go.Scatter(x=[2011.5],y=[13800],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='Space Shuttle last flight in July 2011<extra></extra>'))

        fig.add_trace(go.Scatter(x=[2006.5],y=[10000],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='Debri caused by Chinese anti-satellite<br>missile test in 2007 (Fengyun-1C)<extra></extra>'))

        fig.add_trace(go.Scatter(x=[2018.5],y=[14800],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='SpaceX launches first batch of<br>60 Starlink satellites into LEO<extra></extra>'))

        return fig

    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''
        return [html.Section(className='content-header',children=[
                    html.H1(children='Spatial Density'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(children=[html.I(className='fa fa-dashboard'),' Home']),
                        html.Li(className='active',children='Spatial Density'),
                    ])
                ]),
                html.Section(className='content',children=[
                    html.Div(className='row',children=[
                        html.Div(className='col-md-8',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Spatial Density'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    dcc.Graph(figure=self.__generate_spatial_density_by_year())
                                ])
                            ])
                        ]),
                        html.Div(className='col-md-4',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Satellite Count in LEO'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    dcc.Graph(figure=self.__generate_satellite_count_by_year())
                                ])
                            ])
                        ])
                    ])
                ])
            ]
