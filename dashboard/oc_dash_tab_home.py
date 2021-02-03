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



class homepage():
    '''
    Shows the homepage
    '''


    def __init__(self):
        '''
        Initialize
        '''

    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''
        return [html.Section(className='content-header',children=[
                    html.H1(children='Home'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(className='active', children=[html.I(className='fa fa-dashboard'),' Home'])
                    ])
                ]),
                html.Section(className='content',children=[
                    html.Div(className='row',children=[
                        html.Div(className='col-md-12',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='Home')
                                ]),
                                html.Div(className='box-body',children=[
                                    html.P("Space, and more specifically low-earth orbit, is about to get a whole lot busier and this is making many concerned. At present, there are about 2,000 operational satellites in low-earth orbit and more than double that in defunct satellites. But last year in October, SpaceX requested permission to launch 30,000 Starlink satellites into low-earth orbit. This is in addition to the 12,000 that already received approval. These satellites have already begun interrupting astronomical observations, creating light pollution and increasing collision risks in an environment where a collision could trigger a chain reaction which not only endangers current and future satellites but also human lives."),
                                    html.P(children=[
                                        "This dashboard consists of a few demonstrations of how congested space has become and where it is going.  This dashboard website is written in Python using ",
                                        html.A(children="Plotly Dash",href="https://plotly.com/dash/", target="_blank"),
                                        ".  The layout for the dashboard comes from ",
                                        html.A(children="AdminLTE", href="https://adminlte.io/", target="_blank"),
                                        ", a free open-source implemenation of Bootstrap. The data used to compile these visuals come from the following sources:"
                                    ]),
                                    html.P(
                                        html.Ul(children=[
                                            html.Li(children=[
                                                html.A(href='https://www.space-track.org/',children="Space-Track.org", target="_blank"),
                                                " - For providing the TLE data",
                                            ]),
                                            html.Li(children=[
                                                html.A(href='https://celestrak.com/SOCRATES/',children="SOCRATES", target="_blank"),
                                                " - For upcoming satellite collision probability detection",
                                            ]),
                                            html.Li(children=[
                                                html.A(href='https://ntrs.nasa.gov/',children="NASA's History of On-Orbit Satellite Fragmentations", target="_blank"),
                                                " - For satellite breakup dates",
                                            ]),
                                        ])
                                    ),
                                    html.P("The following additional Python libaries are used by this dashboard:"),
                                    html.P(
                                        html.Ul(children=[
                                            html.Li(html.A("Pandas", href='https://pypi.org/project/pandas/', target="_blank")),
                                            html.Li(html.A("Numpy", href='https://pypi.org/project/numpy/', target="_blank")),
                                            html.Li(html.A("Plotly", href='https://plotly.com/', target="_blank")),
                                            html.Li(html.A("Matplotlib", href='https://matplotlib.org/', target="_blank")),
                                            html.Li(html.A("Satellite-CZML", href='https://pypi.org/project/satellite-czml/', target="_blank"))
                                        ])
                                    ),
                                    html.P(children=[
                                        "This dashboard also uses CersiumJS for some of the visualziations.  ",
                                        html.A("CesiumJS", href='https://cesium.com/cesiumjs/', target="_blank"),
                                        " is an open source JavaScript library for creating a 3D map of the earth and creates interactive animations using their CZML language written in JSON."
                                    ]),
                                    html.P("This work is a collaboration of the following individuals (surname in alphabetical order):"),
                                    html.P(
                                        html.Ul(children=[
                                            html.Li(html.A(href='https://github.com/timzai',children="Tim Chen", target="_blank")),
                                            html.Li(html.A(href='https://github.com/sophde',children="Sophie Deng", target="_blank")),
                                            html.Li(html.A(href='https://github.com/cassova',children="Nicholas Miller", target="_blank")),
                                        ])
                                    ),
                                    html.P(children=[
                                        "For the full report of the analysis, please ",
                                        html.A(href='https://mads-hatters.github.io/',children="Click Here", target="_blank"),
                                        ". The code for this dashboard and the report are open source under the MIT license and can be found ",
                                        html.A(href='https://github.com/mads-hatters/SIADS-591-Orbital-Congestion',children="Here", target="_blank"),
                                    ]),
                                    html.P(children=[
                                        html.B("Suggested citation: "),
                                        "Chen-Deng-Miller, Orbital Congestion, 3 Feb 2021, Retrieved from: https://oc-dash.herokuapp.com/"
                                    ]),
                                ])
                            ])
                        ])
                    ])
                ])
            ]
