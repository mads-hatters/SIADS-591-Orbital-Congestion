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



class history():
    '''
    Shows spatial density and related graphics
    '''

    sat_df = None
    obj_df = None
    dec_df = None
    xgb_df = None

    def __init__(self, sat_df):
        '''
        Initialize
        '''
        self.sat_df = sat_df

    def __load_more_data(self):
        '''
        This loads data for additional visualizations
        '''
        # Using NORAD instead of INTLDES.
        # LAUNCH_DATE has exist_date built in from oc_dash_load

        # count the total number of objects per object type per year
        gb = pd.DataFrame(self.sat_df.groupby(['OBJECT_TYPE', 'LAUNCH_DATE'])['NORAD_CAT_ID'].count()).copy()
        gb.columns = ['Count']
        gb.reset_index(inplace=True)
        gb['year'] = gb['LAUNCH_DATE'].dt.year
        gb = gb[gb['OBJECT_TYPE']!='TBA']
        gb['OBJECT_TYPE'] = gb['OBJECT_TYPE'].apply(lambda x: 'DEBRIS' if x=='ROCKET BODY' else x)
        gb1 = pd.DataFrame(gb.groupby(['OBJECT_TYPE', 'year'])['Count'].sum()).groupby(level=0).cumsum().reset_index()

        # count the number of decay per object per year
        gb_decay = pd.DataFrame(self.sat_df.groupby(['OBJECT_TYPE', 'DECAY_DATE'])['NORAD_CAT_ID'].count()).copy()
        gb_decay.columns = ['Count']
        gb_decay.reset_index(inplace=True)
        gb_decay['year'] = gb_decay['DECAY_DATE'].dt.year
        gb_decay = gb_decay[gb_decay['OBJECT_TYPE']!='TBA']
        gb_decay['OBJECT_TYPE'] = gb_decay['OBJECT_TYPE'].apply(lambda x: 'DEBRIS' if x=='ROCKET BODY' else x)
        gb_decay1 = pd.DataFrame(gb_decay.groupby(['OBJECT_TYPE', 'year'])['Count'].sum()).groupby(level=0).cumsum().reset_index()

        obj_count = pd.merge(gb1, gb_decay1, on=['year','OBJECT_TYPE'], how='outer')
        obj_count['Count_y'] = obj_count['Count_y'] .fillna(0)
        obj_count['Count_x'] = obj_count['Count_x'] .fillna(0)
        obj_count['live'] = obj_count['Count_x'] - obj_count['Count_y']
        obj_count.rename(columns={'Count_x': 'Total', 'Count_y':'Decay'},inplace=True)

        self.obj_df = obj_count
        self.dec_df = gb_decay1
        self.xgb_df = gb1


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

        for y in np.arange(start,2022):
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

        fig.add_trace(go.Scatter(x=[1998.5],y=[7750],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='First segment of ISS is launched into orbit<extra></extra>'))

        fig.add_trace(go.Scatter(x=[2011.5],y=[13800],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='Space Shuttle last flight in July 2011<extra></extra>'))

        fig.add_trace(go.Scatter(x=[2006.5],y=[10000],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='Debri caused by Chinese anti-satellite<br>missile test in 2007 (Fengyun-1C)<extra></extra>'))

        fig.add_trace(go.Scatter(x=[2018.5],y=[14800],showlegend=False,marker=dict(size=12,color='green'),
                                 hovertemplate='SpaceX launches first batch of<br>60 Starlink satellites into LEO<extra></extra>'))

        return fig

    def __generate_satellite_growth_by_year(self):
        '''
        Plot time series data: number of debris and payload 
        from 1958 to 2020.
        inputs: live (df), decay(df), 
        live_col: string
        y1, y2, ax, ay: position of the annotations and arrows

        '''

        # Setup variables
        df = self.obj_df
        decay = self.dec_df
        col_name = 'live'
        extra_df = self.xgb_df
        extra_col = 'Count'

        # Changed some positions around so annotations look nice
        p1 = 12000 # end arrow for 2007-Debris
        p2 = 15000 # end arrow for 2009-Debris
        q1 = 29000 # end arrow for 2007-Total Debris
        q2 = 32000 # end arrow for 2009-Total Debris
        ax = -250
        ay = -60
        ax2 = -60 # for 2009-Debris
        ay2 = -100 # for 2009-Debris
        ax3 = -250 # for 2007-Total Debris
        ay3 = 15 # for 2007-Total Debris
        ax4 = -70
        ay4 = -40

        x1 = df[df['OBJECT_TYPE']=='DEBRIS']['year']
        y1 = df[df['OBJECT_TYPE']=='DEBRIS'][col_name]
        x2 = df[df['OBJECT_TYPE']=='PAYLOAD']['year']
        y2 = df[df['OBJECT_TYPE']=='PAYLOAD'][col_name]
        x3 = decay[decay['OBJECT_TYPE']=='DEBRIS']['year']
        y3 = decay[decay['OBJECT_TYPE']=='DEBRIS']['Count']
        x4 = decay[decay['OBJECT_TYPE']=='PAYLOAD']['year']
        y4 = decay[decay['OBJECT_TYPE']=='PAYLOAD']['Count']

        x5, x6, y5, y6 = None, None, None, None
        if not extra_df.empty:
            x5 = extra_df[extra_df['OBJECT_TYPE']=='DEBRIS']['year']
            y5 = extra_df[extra_df['OBJECT_TYPE']=='DEBRIS'][extra_col]
            x6 = extra_df[extra_df['OBJECT_TYPE']=='PAYLOAD']['year']
            y6 = extra_df[extra_df['OBJECT_TYPE']=='PAYLOAD'][extra_col]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x1, y=y1,name='Debris in Orbit', line=dict(color='crimson')))
        fig.add_trace(go.Scatter(x=x3, y=y3,name='Debris Decay', line=dict(color='crimson', dash='dot')))
        fig.add_trace(go.Scatter(x=x2, y=y2,name='Payload in Orbit', line=dict(color='dodgerblue')))
        fig.add_trace(go.Scatter(x=x4, y=y4,name='Payload Decay', line=dict(color='dodgerblue', dash='dot')))
        fig.add_annotation(x=2007, y=p1, text='2007:Destruction of'+ '<br>'+ 'Chinese satellite by missile',showarrow=True,arrowhead=3,ax=ax, ay=ay,xanchor='right',yanchor='bottom', arrowcolor='grey')
        fig.add_annotation(x=2009 , y=p2, text='',showarrow=True,arrowhead=2,ax=ax2, ay=ay2,xanchor='right',yanchor='bottom',arrowcolor='darkgrey')

        if not extra_df.empty:
            fig.add_trace(go.Scatter(x=x5, y=y5,name='Total Debris', line=dict(color='firebrick')))
            fig.add_trace(go.Scatter(x=x6, y=y6,name='Total Payload', line=dict(color='royalblue')))
            fig.add_annotation(x=2007, y=q1, text='',showarrow=True,arrowhead=3,ax=ax3, ay=ay3,xanchor='right',yanchor='bottom', arrowcolor='grey')
            fig.add_annotation(x=2009 , y=q2, text='2009:Accidental collision'+ '<br>'+ 'of US and Russian satellites',showarrow=True,arrowhead=2,ax=ax4,ay=ay4,xanchor='right',yanchor='bottom', arrowcolor='darkgrey')


        x_ticks = list(np.arange(1958, 2020, 3))
        fig.update_layout(xaxis = dict(tickmode = 'array', tickvals = x_ticks), xaxis_range=[1958,2020],
                          title={'text':'Growth of Space Objects','x':0.4,'y':0.85}, 
                                 xaxis_title='Year', yaxis_title = "Number of items")
        return fig

    def __generate_objects_by_orbit(self):
        df4 = self.sat_df.copy()
        df4['year_exist'] = df4['LAUNCH_DATE'].dt.year
        orbit_type = pd.DataFrame(df4.groupby(['Orbit','year_exist'])['NORAD_CAT_ID'].count()).groupby(level=0).cumsum().reset_index()
        orbit_type.rename(columns={'NORAD_CAT_ID':'count'}, inplace=True)
        x_ticks = list(np.arange(1958, 2020, 3))
        fig = px.bar(orbit_type, x='year_exist', y='count', color='Orbit', 
                     labels={'year_exist': 'Year', "count":"Number of Ojects"},
                      range_x=[1958,2020.5])
        fig.update_layout(title={'text': "Number of Space Objects in Different Orbits",
                                 'x':0.5, 'y':0.92}, barmode="stack",
                         xaxis = dict(tickmode = 'array', tickvals = x_ticks))
        return fig

    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''
        self.__load_more_data()

        return [html.Section(className='content-header',children=[
                    html.H1(children='History'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(children=[html.I(className='fa fa-dashboard'),' Home']),
                        html.Li(className='active',children='History'),
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
                                    html.P("The spatial density of LEO and how it has changed over time.  Each altitude represents a 10km thickness of space around the Earth."),
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
                                    html.P("Number of objects in orbit around the Earth for given year.  This considers objects that are no longer in orbit."),
                                    dcc.Graph(figure=self.__generate_satellite_count_by_year())
                                ])
                            ])
                        ])
                    ]),
                    html.Div(className='row',children=[
                        html.Div(className='col-md-6',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Growth of Space Objects'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.P("How the cumulative count of objects in space has changed over time."),
                                    dcc.Graph(figure=self.__generate_satellite_growth_by_year())
                                ])
                            ])
                        ]),
                        html.Div(className='col-md-6',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Space Objects by Orbit'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.P("Cumulative figures of all objects put into space by their orbit."),
                                    dcc.Graph(figure=self.__generate_objects_by_orbit())
                                ])
                            ])
                        ])
                    ])
                ])
            ]
