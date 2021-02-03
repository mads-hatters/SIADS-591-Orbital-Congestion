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
                        html.P("AQUA performed multiple orbit raising and inclination adjustment maneuvers as seen here.  The sensitivity of the maneuver thresholds all hold up rather well for the majority of the cases.  The orbit raising and lowering maneuvers were detected correctly, however there were some false positives for the sensitive 10 and 20 rolling neighbor inclination adjustment detection."),
                        html.Img(src='./assets/AQUA (27424).png'),
                        html.P("When the combined detection method using `rolling_10_neighbor_diff` with 0.008 threshold for inclination and `rolling_3_neighbor_diff` with 0.025 threshold for semimajor axis was used, three maneuvers in early 2010 were missed."),
                        html.Img(src='./assets/AQUA (27424)_combined.png')
                   ])
        elif tab == 'maneuver-cosmos':
            return html.Div(children=[
                        html.P("The COSMOS 2251 actually do not have a propulsion system, however, its orbit did change due to its collision with IRIDIUM-33 in 2009. Examining it's entire life span will also allows for the evaluation of the maneuver detection method over a long period of time. A lot of false positives can be seen in some of the thresholds.  It is also interesting to note that the cluster of mis-identification for semimajor axis coincides with increased solar activity during 2001, 2003, and 2014.  The solar activity in 2001 and 2003 was significantly stronger, and can be visually identified, while the 2011 was relatively weaker and did not pass the thresholds."),
                        html.Img(src='./assets/COSMOS 2251 (22675).png'),
                        html.P("Expecting only a single event representing the collision, we saw 2 cases of false positives due to potential outliers in the data."),
                        html.Img(src='./assets/COSMOS 2251 (22675)_combined.png')
                   ])
        elif tab == 'maneuver-gcom':
            return html.Div(children=[
                        html.P("NASA documented 5 RMMs during the indicated time range, in 2016/06/08, 2016/9/30, 2017/01/11, 2017/05/30, and 2017/07/06.  Other maneuvers can be spotted as well.  The magnitude of the maneuvers differ greatly for each event and the two lesser ones are only picked up by the most sensitive thresholds."),
                        html.Img(src='./assets/GCOM W1 (38337).png'),
                        html.P("Ground truth data for all maneuvers are not completely available, however, we can be sure that the 2017/05/30 RMM failed to be detected successfully."),
                        html.Img(src='./assets/GCOM W1 (38337)_combined.png')
                   ])
        elif tab == 'maneuver-glast':
            return html.Div(children=[
                        html.P("NASA revealed that the Fermi Telescope performed an evasive maneuver in April of 2012.  It had not performed any other maneuvers prior to this since being put in orbit.  As seen here, the more sensitive thresholds picked up lots of activity, possibly due to the satellite rotating survey different parts of the sky."),
                        html.Img(src='./assets/GLAST (33053).png'),
                        html.P("Multiple false positives were picked up, with the earlier ones attributed to the solar maxima of 2011."),
                        html.Img(src='./assets/GLAST (33053)_combined.png')
                   ])
        elif tab == 'maneuver-iss':
            return html.Div(children=[
                        html.P("The ISS is the largest artificial object in space.  Due to its low orbit, it performs many maneuvers to re-raise its orbit.  It has also performed many RMMs previously."),
                        html.Img(src='./assets/ISS (ZARYA) (25544).png'),
                        html.P("Ground truth maneuvering data for ISS maneuvers is unavailable, however, it looks like the major maneuvers were picked up, with a few potential false positives."),
                        html.Img(src='./assets/ISS (ZARYA) (25544)_combined.png')
                   ])
        elif tab == 'maneuver-oco':
            return html.Div(children=[
                        html.P("OCO-2 performed multiple orbit raising and inclination maneuvers in the selected period.  It's semimajor axis and inclination data looks to be very clean and easy to pick out maneuvers."),
                        html.Img(src='./assets/OCO 2 (40059).png'),
                        html.P("Successfully detected all maneuvers, with no errors."),
                        html.Img(src='./assets/OCO 2 (40059)_combined.png')
                   ])
        elif tab == 'maneuver-payloadc':
            return html.Div(children=[
                        html.P("PAYLOAD C, or Shiyan 7 (SY-7, Experiment 7) is a Chinese satellite that possesses the ability to greatly alter its orbit rapidly, it made a series of big maneuvers in its first 3 years of service and continued to make tiny adjustments after that.  Note the scale of y-axis here is significantly wider than most other examined satellies."),
                        html.Img(src='./assets/PAYLOAD C (39210).png'),
                        html.P("Shiyan 7's big maneuvers were all identified, however, other positive matches were inconclusive because of the lack of ground truth data."),
                        html.Img(src='./assets/PAYLOAD C (39210)_combined.png')
                   ])
        elif tab == 'maneuver-starlink':
            return html.Div(children=[
                        html.P("A Starlink was included due to SpaceX being one of the main contributors for recent increase in Low Earth Orbit satellites. STARLINK-1007 is amongst the first operational Block v1.0 Starlinks that were launched.  Note that the parking orbit is significantly lower than it's operational orbit, with the change in semimajor axis greater than even that of Shiyan 7.  As seen in the chart below, the orbit raising and lowering maneuver detection failed to produce any meaning results, this may be due their required operational parameters."),
                        html.Img(src='./assets/STARLINK-1007 (44713).png'),
                        html.P("Starlinks were detected as being constantly maneuvering. After cross-checking this with other Starlinks, it would appear that unlike other satellites where they would allow their orbit to decay and do occasional adjustments, Starlinks actually are constantly re-adjusting their orbits."),
                        html.Img(src='./assets/STARLINK-1007 (44713)_combined.png')
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
                                        dcc.Tab(label='STARLINK-1007', value='maneuver-starlink'),
                                    ]),
                                ]),
                                html.Div(id='tab-content')
                            ])
                        ])
                    ])
                ])
            ]
