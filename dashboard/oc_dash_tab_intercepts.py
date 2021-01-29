# Orbital Congestion Dashboard
# Written by Nicholas Miller

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format

from datetime import date, timedelta

import oc_dash_load
import oc_dash_utils

from satellite_czml import satellite_czml



class intercepts():
    '''
    Shows intercepts of satellites using SOCRATES and TLE data 
    '''

    # Intercept Table Columns
    intercept_columns = [{'id': 'sat_pair', 'name': 'Satellite Pair'},
                         {'id': 'tca_time', 'name': 'Intercept Date/Time'},
                         {'id': 'max_prob', 'name': 'Max Probabilty (%)', 'type': 'numeric', 'format': FormatTemplate.percentage(5)},
                         {'id': 'min_rng_km', 'name': 'Minimum Distance (km)', 'type': 'numeric', 'format': Format(precision=5)},
                         {'id': 'rel_velo_kms', 'name': 'Relative Velocity (kms)', 'type': 'numeric', 'format': Format(precision=5)},
                         {'id': 'index', 'name': 'Index'}]

    intercept_df = None
    sat_df = None

    def __init__(self, intercept_df, sat_df):
        '''
        Initialize
        '''
        self.intercept_df = intercept_df
        self.sat_df = sat_df

    def generate_intercept_table(self, start_date, end_date, max_prob, min_dist, sat_name):
        '''
        Generates the table on the dashboard that displays intercepts
        '''
        if start_date is None:
            start_date_obj = min(self.intercept_df['tca_time'].dt.date)
        else:
            start_date_obj = date.fromisoformat(start_date)

        if end_date is None:
            end_date_obj = max(self.intercept_df['tca_time'].dt.date)
        else:
            end_date_obj = date.fromisoformat(end_date)

        if sat_name is None:
            sat_name = ''

        df = self.intercept_df[(self.intercept_df['tca_time'].dt.date >= start_date_obj) &
                    (self.intercept_df['tca_time'].dt.date <= end_date_obj) &
                    (self.intercept_df['max_prob'] >= max_prob[0]) & 
                    (self.intercept_df['max_prob'] <= max_prob[1]) & 
                    (self.intercept_df['min_rng_km'] >= min_dist[0]) & 
                    (self.intercept_df['min_rng_km'] <= min_dist[1]) &
                    (self.intercept_df['sat_pair'].str.contains(sat_name.upper()))]
        return df.reset_index().to_dict('records')

    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''
        return [
                html.Section(className='content-header',children=[
                    html.H1(children='Intercepts'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(children=[html.I(className='fa fa-dashboard'),' Home']),
                        html.Li(className='active',children='Intercepts'),
                    ])
                ]),
                html.Section(className='content',children=[
                    html.Div(className='row',children=[
                        html.Div(className='col-md-12',children=[
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
                                        html.P("This is a visualization tool used animate two satellites that came within close proximity of eachother for a specific date/time.  Choose a date range or try some of the other filtering criteria.  The table on the right will update the top close-encounters as reported by SOCRATES on that day for your filter criteria.  The table is automatically sorted by highest priority.  Select one of the satellite pairs to visualize them below using Cesium's 3D world viewer and watch them animate as they come within close proximity of eachother."),
                                        html.P("SUGGESTION: specify a window of 1 week or less to not overload the server.  If the table returns nothing, make sure the sliders aren't overly restrictive and try a smaller date range."),
                                    ])
                                ])
                            ])
                        ])
                    ]),
                    html.Div(className='row',children=[
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
                                        html.Table(className='table', children=[
                                            html.Tr(children=[
                                                html.Th(children='Date'),
                                                html.Td(children=[
                                                    ##########################################################
                                                    # Date Picker
                                                    dcc.DatePickerRange(
                                                        id='date-picker',
                                                        with_portal=True,
                                                        minimum_nights=0,
                                                        min_date_allowed=min(self.intercept_df['tca_time'].dt.date),
                                                        start_date=min(self.intercept_df['tca_time'].dt.date),
                                                        end_date=min(self.intercept_df['tca_time'].dt.date),
                                                        max_date_allowed=max(self.intercept_df['tca_time'].dt.date),
                                                        initial_visible_month=min(self.intercept_df['tca_time'].dt.date)
                                                    )
                                                ])
                                            ]),
                                            html.Tr(children=[
                                                html.Th(children='Max Probability'),
                                                html.Td(children=[
                                                    html.Div(style={'padding': '20px 0px 0px'}, children=[
                                                        ##########################################################
                                                        # Max Probability Range Slider
                                                        dcc.RangeSlider(
                                                            id='max-prob-slider',
                                                            min=min(self.intercept_df['max_prob']),
                                                            max=max(self.intercept_df['max_prob']),
                                                            step=0.001,
                                                            value=[min(self.intercept_df['max_prob']), max(self.intercept_df['max_prob'])],
                                                            tooltip={'always_visible': True, 'placement': 'bottom'}
                                                        )
                                                    ])
                                                ])
                                            ]),
                                            html.Tr(children=[
                                                html.Th(children='Min Distance'),
                                                html.Td(children=[
                                                    html.Div(style={'padding': '20px 0px 0px'}, children=[
                                                        ##########################################################
                                                        # Min Distance Range Slider
                                                        dcc.RangeSlider(
                                                            id='min-dist-slider',
                                                            min=min(self.intercept_df['min_rng_km']),
                                                            max=max(self.intercept_df['min_rng_km']),
                                                            step=0.001,
                                                            value=[min(self.intercept_df['min_rng_km']), max(self.intercept_df['min_rng_km'])],
                                                            tooltip={'always_visible': True, 'placement': 'bottom'}
                                                        )
                                                    ])
                                                ])
                                            ]),
                                            html.Tr(children=[
                                                html.Th(children=[
                                                    html.Div(style={'padding': '20px 0px 0px'}, children=['Satellite Name'])
                                                ]),
                                                html.Td(children=[
                                                    html.Div(style={'padding': '20px 0px 0px'}, children=[
                                                        ##########################################################
                                                        # Satellite Name
                                                        dcc.Input(
                                                            id='satellite-name',
                                                            type='text',
                                                            className='form-control input-lg',
                                                            placeholder='e.g. Starlink'
                                                        )
                                                    ])
                                                ])
                                            ]),
                                        ])
                                    ])
                                ])
                            ])
                        ]),
                        html.Div(className='col-md-8',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Intercept Table'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        ##########################################################
                                        # Intercept Table
                                        dcc.Loading(id='intercept-table-load', type="circle", children=[
                                            dash_table.DataTable(
                                                id='intercept-table',
                                                columns=self.intercept_columns,
                                                style_as_list_view=True,
                                                style_header={
                                                    'backgroundColor': 'white',
                                                    'fontSize': '14px',
                                                    'fontWeight': 'bold',
                                                    'textAlign': 'left'
                                                },
                                                style_cell={
                                                    'padding': '0px',
                                                    'fontSize': '12px',
                                                    'textAlign': 'left'
                                                },
                                                row_selectable="single",
                                                page_size=10,
                                                sort_action="native",
                                                selected_rows=[],
                                                hidden_columns=['index']
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
                                    html.H3(className='box-title',children='Intercepting Orbits')
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        ##########################################################
                                        # Cesium
                                        dcc.Loading(id='cesium-intercept', type="circle", children=[
                                            html.Div(id='cesiumContainer'),
                                            html.Div(id='czml', style={'display': 'none'})
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ]


    def generate_intercept_czml(self, rows, index):
        '''
        Generates the CZML (time animation) in Cesium of the intercept
        '''
        if index is not None and len(index) > 0:
            u = oc_dash_utils.utils(self.intercept_df, self.sat_df)
            idx = rows[index[0]]['index']

            sat_names = [self.intercept_df.loc[idx]['sat1_name'], self.intercept_df.loc[idx]['sat2_name']]
            sat_tles = [self.intercept_df.loc[idx]['sat1_tle'].split(','),
                        self.intercept_df.loc[idx]['sat2_tle'].split(',')]
            sat_descs = [u.generate_satellite_description(row=self.intercept_df.loc[idx], sat='sat1'),
                         u.generate_satellite_description(row=self.intercept_df.loc[idx], sat='sat2')]

            start_time = self.intercept_df.loc[idx]['tca_time'] - timedelta(hours = 0.5)
            end_time = self.intercept_df.loc[idx]['tca_time'] + timedelta(hours = 0.5)
            czml = satellite_czml(tle_list=sat_tles, start_time=start_time, end_time=end_time,
                                  name_list=sat_names, description_list=sat_descs).get_czml()

            return czml
