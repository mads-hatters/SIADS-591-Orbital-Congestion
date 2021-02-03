# Orbital Congestion Dashboard
# Written by Nicholas Miller

import dash
import dash_html_components as html



class gabbard():
    '''
    Shows Gabbard video
    '''

    base_url = 'https://www.youtube.com/embed/mQT5aMa_7iI'

    def __init__(self):
        '''
        Initialize
        '''

    def get_page_content(self):
        '''
        Generates the dashboard page content
        '''

        return [html.Section(className='content-header',children=[
                    html.H1(children='Gabbard Diagram'),
                    html.Ol(className='breadcrumb',children=[
                        html.Li(children=[html.I(className='fa fa-dashboard'),' Home']),
                        html.Li(className='active',children='Gabbard Diagram'),
                    ])
                ]),
                html.Section(className='content',children=[
                    html.Div(className='row',children=[
                        html.Div(className='col-md-12',children=[
                            html.Div(className='box',children=[
                                html.Div(className='box-header with-border',children=[
                                    html.H3(className='box-title',children='History of LEO till January 2021')
                                ]),
                                html.Div(className='box-body',children=[
                                    html.P("John Gabbard developed a diagram for illustrating the orbital changes and the orbital decay of debris fragments. A Gabbard diagram is a scatter plot of orbit altitude versus orbital period. Since all orbits are elliptical, a Gabbard diagram plots two points for each satellite: the apogee and perigee. Each pair of points will share the same orbital period and thus will be vertically aligned."),
                                    html.P(children=[
                                        html.Ul(children=[
                                            html.Li(html.A(href=self.base_url + '?autoplay=1&loop=1&rel=0&fs=1&start=45&end=56', target="gabbard_video", children="October 1970 - Cosmos 374 & 375 Deliberate Self-Destruct")),
                                            html.Li(html.A(href=self.base_url + '?autoplay=1&loop=1&rel=0&fs=1&start=104&end=115', target="gabbard_video", children="September 1985 - P-78/Solwind Destroyed by Anti-Satellite Weapon")),
                                            html.Li(html.A(href=self.base_url + '?autoplay=1&loop=1&rel=0&fs=1&start=147&end=159', target="gabbard_video", children="June 1996 - Step II Rocket Body Propulsion System Failure")),
                                            html.Li(html.A(href=self.base_url + '?autoplay=1&loop=1&rel=0&fs=1&start=190&end=201', target="gabbard_video", children="January 2007 - Fengyun 1C Destroyed by Anti-Satellite Weapon")),
                                            html.Li(html.A(href=self.base_url + '?autoplay=1&loop=1&rel=0&fs=1&start=199&end=210', target="gabbard_video", children="February 2009 - Iridium 33 & Cosmos 2251 Collision")),
                                            html.Li(html.A(href=self.base_url + '?autoplay=1&loop=1&rel=0&fs=1&start=240&end=251', target="gabbard_video", children="March 2019 - Microsat-R Destroyed by Anti-Satellite Weapon")),
                                        ])
                                    ]),
                                    html.Iframe(id='igabbard', name='gabbard_video', width="800", height="500", src=self.base_url + "?autoplay=1&loop=1&rel=0&fs=1", style=dict(border=0))
                                ])
                            ])
                        ])
                    ])
                ])
            ]
