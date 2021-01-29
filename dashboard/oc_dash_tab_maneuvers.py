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
            return html.Img(src='images/AQUA (27424).png')
        elif tab == 'maneuver-cosmos':
            return html.Img(src='images/AQUA (27424).png')
        elif tab == 'maneuver-gcom':
            return html.Img(src='images/AQUA (27424).png')
        elif tab == 'maneuver-glast':
            return html.Img(src='images/AQUA (27424).png')
        elif tab == 'maneuver-iss':
            return html.Img(src='images/AQUA (27424).png')
        elif tab == 'maneuver-oco':
            return html.Img(src='images/AQUA (27424).png')
        elif tab == 'maneuver-payloadc':
            return html.Img(src='images/AQUA (27424).png')


    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''

        return [html.Section(className='content-header',children=[
                    html.H1(children='History'),
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
                                    html.H3(className='box-title',children='Maneuver Detection'),
                                    html.Div(className='box-tools pull-right', children=[
                                        html.Button(className='btn btn-box-tool', **{'data-widget': 'collapse'}, children=[
                                            html.I(className='fa fa-minus')
                                        ])
                                    ])
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
