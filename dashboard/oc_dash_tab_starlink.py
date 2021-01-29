# Orbital Congestion Dashboard
# Written by Nicholas Miller
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq

import random

from satellite_czml import satellite_czml



class starlink():
    '''
    Shows starlink satellite data
    '''

    sat_df = None

    def __init__(self, sat_df):
        '''
        Initialize
        '''
        self.sat_df = sat_df

    def generate_starlink_czml(self, show_path=False):
        '''
        Generates the CZML for the starlink satellites
        '''
        df = self.sat_df[(self.sat_df['OBJECT_ID'].notnull()) & (self.sat_df['DECAY_DATE'].isnull() & self.sat_df['OBJECT_NAME'].str.startswith('STARLINK'))].copy()

        random.seed(0)
        color_by='LAUNCH_DATE'
        group_colors = {x: [random.randrange(256) for x in range(3)] for x in df[color_by].unique()}
        for c in group_colors.values():
            c.append(128)
        df['color'] = df[color_by].map(group_colors)

        sat_colors = df['color'].to_list()
        sat_names = df['OBJECT_NAME'].to_list()
        sat_tles = df[['TLE_LINE1', 'TLE_LINE2']].values.tolist()
        sat_group = df[color_by].to_list()
        sat_descs = df['description'].to_list()
        sat_size = [7] * len(sat_tles)

        czml_obj = satellite_czml(tle_list=sat_tles, name_list=sat_names, description_list=sat_descs,
                                  color_list=sat_colors, speed_multiplier=1, use_default_image=False,
                                  marker_scale_list=sat_size, show_label=False, show_path=show_path,
                                  ignore_bad_tles=False)
        return czml_obj.get_czml()

    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''
        return [html.Section(className='content-header',children=[
                    html.H1(children='Starlink Satellites'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(children=[html.I(className='fa fa-dashboard'),' Home']),
                        html.Li(className='active',children='Starlink Satellites'),
                    ])
                ]),
                html.Section(className='content',children=[
                    html.Div(className='row',children=[
                        html.Div(className='col-md-8',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='About'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        html.P("This is a visualization of all 951 SpaceX's Starlink satellites in orbit as of January 2021.  Starlink intends to launch another 11,000 satellites by 2027 and has requested permission to launch another 30,000 after that."),
                                        html.P("Satellites launched on the same date have the same color.  While it appears the satellites aren't moving, they actually are.  Try zooming in or increasing the animation speed by adjusting the green arrow on the dial in the bottom left corner.  Enable the path switch on the right to visualize the orbit path of each satellite.  Due to the amount of data, performance will likely be impacted so please keep this disabled if you experience issues."),
                                        html.P("Disclaimer: The position of the satellites is based on out-dated TLE data so it is unlikely the animation you're seeing today is a true reflection of where the satellites are in relation to the earth.")
                                    ])
                                ])
                            ])
                        ]),
                        html.Div(className='col-md-4',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Filter'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        html.Center(children=[
                                            ##########################################################
                                            # Show Orbit Path Switch
                                            daq.BooleanSwitch(
                                                id='show-orbit-path',
                                                label="Show Path",
                                                on=False
                                            )
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ]),
                    html.Div(className='row',children=[
                        html.Div(className='col-md-12',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Starlink Satellites'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        ##########################################################
                                        # Cesium
                                        dcc.Loading(id='cesium-starlink', type="circle", children=[
                                            html.Div(id='cesiumContainer2'),
                                            html.Div(id='czml2', style={'display': 'none'})
                                        ]),
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ]
