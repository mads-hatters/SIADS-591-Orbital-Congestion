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



class maneuvers():
    '''
    Shows maneuver detection data
    '''

    def __init__(self):
        '''
        Initialize
        '''
    def get_tab_content(self, tab):
        if tab == 'maneuver-aqua':
            return html.Div(children=[
                        html.Img(src='./assets/AQUA (27424).png'),
                        html.P("Description of above image"),
                        html.Img(src='./assets/AQUA (27424)_combined.png'),
                        html.P("Description of above image")
                   ])
        elif tab == 'maneuver-cosmos':
            return html.Div(children=[
                        html.Img(src='./assets/COSMOS 2251 (22675).png'),
                        html.P("Description of above image"),
                        html.Img(src='./assets/COSMOS 2251 (22675)_combined.png'),
                        html.P("Description of above image")
                   ])
        elif tab == 'maneuver-gcom':
            return html.Div(children=[
                        html.Img(src='./assets/GCOM W1 (38337).png'),
                        html.P("Description of above image"),
                        html.Img(src='./assets/GCOM W1 (38337)_combined.png'),
                        html.P("Description of above image")
                   ])
        elif tab == 'maneuver-glast':
            return html.Div(children=[
                        html.Img(src='./assets/GLAST (33053).png'),
                        html.P("Description of above image"),
                        html.Img(src='./assets/GLAST (33053)_combined.png'),
                        html.P("Description of above image")
                   ])
        elif tab == 'maneuver-iss':
            return html.Div(children=[
                        html.Img(src='./assets/ISS (ZARYA) (25544).png'),
                        html.P("Description of above image"),
                        html.Img(src='./assets/ISS (ZARYA) (25544)_combined.png'),
                        html.P("Description of above image")
                   ])
        elif tab == 'maneuver-oco':
            return html.Div(children=[
                        html.Img(src='./assets/OCO 2 (40059).png'),
                        html.P("Description of above image"),
                        html.Img(src='./assets/OCO 2 (40059)_combined.png'),
                        html.P("Description of above image")
                   ])
        elif tab == 'maneuver-payloadc':
            return html.Div(children=[
                        html.Img(src='./assets/PAYLOAD C (39210).png'),
                        html.P("Description of above image"),
                        html.Img(src='./assets/PAYLOAD C (39210)_combined.png'),
                        html.P("Description of above image")
                   ])


    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''

        return [html.Section(className='content-header',children=[
                    html.H1(children='Maneuver Detection'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(children=[html.I(className='fa fa-dashboard'),' Home']),
                        html.Li(className='active',children='Maneuver Detection'),
                    ])
                ]),
                html.Section(className='content',children=[
                    html.Div(className='row',children=[
                        html.Div(className='col-md-12',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Maneuver Detection')
                                ]),
                                html.Div(className='box-body',children=[
                                    html.P("A few noval approaches were attempted to detect satellite maneuvers as demonistrated in the following images."),
                                    dcc.Tabs(id="maneuver-tabs", value='maneuver-aqua', children=[
                                        dcc.Tab(label='AQUA', value='maneuver-aqua'),
                                        dcc.Tab(label='COSMOS 2251', value='maneuver-cosmos'),
                                        dcc.Tab(label='GCOM W1', value='maneuver-gcom'),
                                        dcc.Tab(label='GLAST', value='maneuver-glast'),
                                        dcc.Tab(label='ISS (ZARYA)', value='maneuver-iss'),
                                        dcc.Tab(label='OCO 2', value='maneuver-oco'),
                                        dcc.Tab(label='PAYLOAD C', value='maneuver-payloadc'),
                                    ]),
                                ]),
                                html.Div(id='tab-content')
                            ])
                        ])
                    ])
                ])
            ]
