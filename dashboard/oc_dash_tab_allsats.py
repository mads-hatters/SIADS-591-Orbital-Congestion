# Orbital Congestion Dashboard
# Written by Nicholas Miller

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format

import plotly.express as px
import plotly.graph_objects as go
import cv2

import numpy as np
import pandas as pd



class allsats():
    '''
    Shows all satellites in around earth today
    '''

    sat_df = None
    earth_fig = None
    table_columns = [{'id': 'group', 'name': 'Group'}]

    def __init__(self, sat_df):
        '''
        Initialize
        '''
        self.sat_df = self.__prepare_data(sat_df)
        self.earth_fig = self.__draw_earth()
    
    def generate_pie_chart(self, color_by='OBJECT_TYPE'):
        '''
        Generates the pie chart based on the color-by selection
        '''
        #tmp_df = self.sat_df.groupby(color_by).count()
        #fig = px.pie(tmp_df, values=color_by, names='index')
        #fig.update_traces(textposition='inside', textinfo='percent+label')
        tmp_df = self.sat_df.groupby(color_by)[['NORAD_CAT_ID']].count().reset_index()
        fig = px.pie(tmp_df, values='NORAD_CAT_ID', names=color_by)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return dcc.Graph(figure=fig)
        
    def generate_group_table(self, color_by='OBJECT_TYPE'):
        '''
        Generates the table of different groups to show to user
        '''
        groups =  [{'group': x} for x in sorted(list(self.sat_df[color_by].unique()))]
        
        return (dash_table.DataTable(
                id='allsat-table-filter',
                columns=self.table_columns,
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
                row_selectable="multi",
                page_size=10,
                sort_action="native",
                data = groups,
                selected_rows=[i for i in range(len(groups))]
            ),
            self.generate_pie_chart(color_by))
    
    def generate_all_sats(self, color_by='OBJECT_TYPE', seed=None, rows=None, indexes=None):
        '''
        Geneates the plotly 3d scatter plot
        '''
        if seed==None or seed == '':
            seed = '20'
        np.random.seed(int(seed))
        
        new_fig = go.Figure(self.earth_fig)
        groups = [rows[i]['group'] for i in indexes]
        fin_fig = self.__draw_satellites(new_fig, color_by, groups)
        return dcc.Graph(figure=fin_fig)

    def select_deselect(self, selbtn, deselbtn, selected_rows):
        '''
        Selects/Deselects all rows in table
        Source: https://community.plotly.com/t/select-all-rows-in-dash-datatable/41466
        '''
        ctx = dash.callback_context
        if ctx.triggered:
            trigger = (ctx.triggered[0]['prop_id'].split('.')[0])
        try:
            if trigger == 'satall-selall':
                if selected_rows is None:
                    return [[]]
                else:
                    return [[i for i in range(len(selected_rows))]]
            else:
                return [[]]
        except:
            # ctx is None
            try:
                return [[i for i in range(len(selected_rows))]]
            except:
                # selected_rows is None
                return [[]]
    
    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''
        return [html.Section(className='content-header',children=[
                    html.H1(children='Satellites Now'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(children=[html.I(className='fa fa-dashboard'),' Home']),
                        html.Li(className='active',children='Satellites Now'),
                    ])
                ]),
                html.Section(className='content',children=[
                    html.Div(className='row',children=[
                        html.Div(className='col-md-4',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Settings'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        html.P("This interactive visualization displays all objects, including debris, in orbit around Earth as of January 2021.  Change the settings below or the filters on the right.  The image is generated with Plotly so there are several interactive elements to be explored."),
                                        html.Table(className='table', children=[
                                            html.Tr(children=[
                                                html.Th('Color by'),
                                                html.Td(children=[
                                                    ##########################################################
                                                    # Color By Drop Down
                                                    dcc.Dropdown(
                                                        id='dd-allsat-colorby',
                                                        className='dropdown-lg',
                                                        options=[
                                                            {'label': 'Object Type', 'value': 'OBJECT_TYPE'},
                                                            {'label': 'Object Size', 'value': 'RCS_SIZE_NAME'},
                                                            {'label': 'Country/Company', 'value': 'country'}
                                                        ],
                                                        value='OBJECT_TYPE',
                                                        clearable=False
                                                    )
                                                ])
                                            ]),
                                            html.Tr(children=[
                                                html.Th('Random Color Seed'),
                                                html.Td(children=[
                                                    html.Div(style={'padding': '20px 0px 0px'}, children=[
                                                        ##########################################################
                                                        # Color Seed
                                                        dcc.Input(
                                                            id='allsat-colorseed',
                                                            type='text',
                                                            className='form-control input-lg',
                                                            placeholder='Default: 20'
                                                        )
                                                    ])
                                                ])
                                            ]),
                                            html.Tr(children=[
                                                html.Th(' '),
                                                html.Td(children=[
                                                    html.Div(style={'padding': '20px 0px 0px'}, children=[' '])
                                                ])
                                            ])
                                        ])
                                    ])
                                ])
                            ])
                        ]),
                        html.Div(className='col-md-4',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Breakdown'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        ##########################################################
                                        # Pie Chart
                                        dcc.Loading(id='allsat-load-pie-chart', type="circle", children=[
                                            html.Div(id='allsat-pie-chart')
                                        ])
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
                                        ##########################################################
                                        # Filter Table
                                        html.Div(className='btn-group', children=[
                                            html.Button('Select All', id='satall-selall', n_clicks=0, className='btn btn-default'),
                                            html.Button('Deselect All', id='satall-desall', n_clicks=0, className='btn btn-default')
                                        ]),
                                        dcc.Loading(id='allsat-table-load', type="circle", children=[
                                            dash_table.DataTable(id='allsat-table-filter')
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
                                    html.H3(className='box-title',children='All Satellites'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
                                ]),
                                html.Div(className='box-body',children=[
                                    html.Div(className='table-responsive',children=[
                                        ##########################################################
                                        # All Satellite 3D Display
                                        dcc.Loading(id='allsat-graph-load', type="circle")
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ]

    def __get_earth_texture(self, size):
        '''
        This sets up the texture that will be used to paint the sphere
        with an image of the earth
        '''
        # Texture
        img = cv2.imread('./assets/cylindrical_sterogrpahic.png')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to greyscale
        img = cv2.resize(img, (size,size), interpolation = cv2.INTER_AREA)  #resize image to match graph linspace
        img = np.fliplr(img) # flip the image
        axis = 1
        #img = np.roll(img, int(img.shape[axis]/2), axis=axis) # roll the image
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE) # rotate the image
        surfcolor = img

        # Coloring
        pl_grey =[[0.0, 'rgb(0, 0, 0)'],
                 [0.05, 'rgb(13, 13, 13)'],
                 [0.1, 'rgb(29, 29, 29)'],
                 [0.15, 'rgb(45, 45, 45)'],
                 [0.2, 'rgb(64, 64, 64)'],
                 [0.25, 'rgb(82, 82, 82)'],
                 [0.3, 'rgb(94, 94, 94)'],
                 [0.35, 'rgb(108, 108, 108)'],
                 [0.4, 'rgb(122, 122, 122)'],
                 [0.45, 'rgb(136, 136, 136)'],
                 [0.5, 'rgb(150, 150, 150)'],
                 [0.55, 'rgb(165, 165, 165)'],
                 [0.6, 'rgb(181, 181, 181)'],
                 [0.65, 'rgb(194, 194, 194)'],
                 [0.7, 'rgb(206, 206, 206)'],
                 [0.75, 'rgb(217, 217, 217)'],
                 [0.8, 'rgb(226, 226, 226)'],
                 [0.85, 'rgb(235, 235, 235)'],
                 [0.9, 'rgb(243, 243, 243)'],
                 [0.95, 'rgb(249, 249, 249)'],
                 [1.0, 'rgb(255, 255, 255)']]
        return surfcolor, pl_grey

    def __draw_earth(self):
        '''
        This creates a 3D plotly graphic with just a sphere with a sterographic
        image of the earth painted on in black-and-white (monochromatic is the
        only option in plotly)
        '''
        size = 400  # resolution of earth - higher looks nicer but its slower
        earth_radius = 6378.

        # Coefficients
        coefs = (1, 1, 1) 
        rx, ry, rz = [earth_radius/np.sqrt(coef) for coef in coefs]

        theta = np.linspace(0,2*np.pi,size)
        phi = np.linspace(0,np.pi,size)
        x = rx * np.outer(np.cos(theta),np.sin(phi))
        y = ry * np.outer(np.sin(theta),np.sin(phi))
        z = rz * np.outer(np.ones(size),np.cos(phi))

        # Earth texture
        surfcolor, pl_grey = self.__get_earth_texture(size)

        data = go.Surface(
            x=x,
            y=y,
            z=z,
            surfacecolor=surfcolor,
            colorscale=pl_grey,
            showscale=False,
            hoverinfo='none',
            contours=go.surface.Contours(
                x=go.surface.contours.X(highlight=False),
                y=go.surface.contours.Y(highlight=False),
                z=go.surface.contours.Z(highlight=False)
            )
        )
        fig = go.Figure(data=data)
        return fig

    def __draw_satellites(self, fig=None, color_by='OBJECT_TYPE', groups=None):
        '''
        This will paint all the satellite dots onto a new or existing
        plotly Figure.
        '''
        # Setup groups
        if groups is None:
            groups = list(self.sat_df[color_by].unique())
        
        # Setup colors
        color_map = {}
        for x in groups:
            rgba = [str(np.random.randint(0,256)) for x in range(3)]
            rgba.append('0.75') #alpha
            color_map[x] = 'rgba(' + ','.join(rgba) + ')'
        self.sat_df['color_by'] = self.sat_df[color_by].map(color_map)

        # setup size
        lim = 100000 #10000

        for group in groups:
            tmp_df = self.sat_df[self.sat_df[color_by] == group]
            data = go.Scatter3d(
                    x=tmp_df['x'].to_list(),
                    y=tmp_df['y'].to_list(),
                    z=tmp_df['z'].to_list(),
                    name=group,
                    hovertemplate = '%{text}',
                    text = tmp_df['allsat_text'].to_list(),
                    mode='markers',
                    marker=dict(
                        color=tmp_df['color_by'].to_list(),
                        size=tmp_df['allsat_marker_size'].to_list(),
                        line=dict(width=0,
                                  color='rgba(255,255,255,0.5)'),
                    )
            )
            if fig is None:
                fig = go.Figure(data=data)
            else:
                fig.add_trace(data)

        fig.update_layout(
            scene = dict(
                bgcolor='black',
                xaxis = dict(
                    visible = False,
                    showticklabels = False,
                    showbackground = False,
                    range = [-1*lim, lim],
                    showspikes=False
                ),
                yaxis = dict(
                    visible = False,
                    showticklabels = False,
                    showbackground = False,
                    range = [-1*lim, lim],
                    showspikes=False
                ),
                zaxis = dict(
                    visible = False,
                    showticklabels = False,
                    showbackground = False,
                    range = [-1*lim, lim],
                    showspikes=False
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1)
            ),
            autosize=True,
            #width=1000,
            height=1000,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='#000000',
                bordercolor='#323232',
                borderwidth=1,
                font=dict(color='#E5E5E5'),
            ),
            margin=go.layout.Margin(
                l=0,
                r=0,
                b=0,
                t=0
            )
        )
        return fig
    
    def __prepare_data(self, df):
        '''
        Prepare the data
        '''
        gpd_df = df.copy()
        
        # Limit satellites to valid enries
        gpd_df = gpd_df[gpd_df['DECAY_DATE'].isnull() & gpd_df['NORAD_CAT_ID'].notnull() & gpd_df['OBJECT_ID'].notnull() & gpd_df['OBJECT_TYPE'].notnull()]
        
        return gpd_df
    
