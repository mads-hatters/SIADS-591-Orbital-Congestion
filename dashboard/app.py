# Orbital Congestion Dashboard
# Written by Nicholas Miller

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import oc_dash_load
from oc_dash_tab_home import homepage
from oc_dash_tab_intercepts import intercepts
from oc_dash_tab_history import history
from oc_dash_tab_starlink import starlink
from oc_dash_tab_allsats import allsats
from oc_dash_tab_maneuvers import maneuvers
from oc_dash_tab_gabbard import gabbard

# Load Spatial Density and intercept datasets
gpd_df, tle_df = oc_dash_load.load_data()

# Setup the differnt tabs to display
tab_home = homepage()
tab_intercept = intercepts(tle_df, gpd_df)
tab_history = history(gpd_df)
tab_starlink = starlink(gpd_df)
tab_allsats = allsats(gpd_df)
tab_maneuvers = maneuvers()
tab_gabbard = gabbard()

# This will style the menu (tabs) to appear correctly
menu_tabs_styles = {
    'borderBottom': '1px solid #222d32',
    'padding': '0px 0px 0px 0px',
    'height': '46px',
    'width':'100%',
    'border': '1px solid',
    'border-color' : '#222d32',
    'width': '230px'
}
menu_tab_style = {
    'border': '1px solid',
    'border-color' : '#222d32',
    'backgroundColor': '#222d32',
    'padding': '15px 5px 15px 15px',
    'display': 'block',
    'font-size': '14px',
    'color': '#b8c7ce',
    'text-align': 'left',
    'font-family': "'Source Sans Pro', 'Helvetica Neue', Helvetica, Arial, sans-serif"
}
menu_tab_selected_style = {
    'border': '1px solid',
    'border-color' : '#2c3b41',
    'backgroundColor': '#2c3b41',
    'padding': '15px 5px 15px 15px',
    'display': 'block',
    'font-size': '14px',
    'color': 'white',
    'text-align': 'left',
    'font-family': "'Source Sans Pro', 'Helvetica Neue', Helvetica, Arial, sans-serif"
}

#-------------------------------------------------------------------------------------
# Generate the dashboard (w/ tabs)
#-------------------------------------------------------------------------------------

external_css = ['http://code.ionicframework.com/ionicons/2.0.0/css/ionicons.min.css',
                'https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css',
                'https://cesium.com/downloads/cesiumjs/releases/1.76/Build/Cesium/Widgets/widgets.css'
               ]

external_scripts = [{'src':'https://cesium.com/downloads/cesiumjs/releases/1.76/Build/Cesium/Cesium.js'}
                   ]

# Initalize the dashboard
app = dash.Dash(__name__, 
                title='Orbital Congestion',
                external_scripts=external_scripts,
                external_stylesheets=external_css)

server = app.server

# Setup the main dashboard with navigation sidebar
app.layout = html.Div(className='skin-blue', children=[
    html.Div(className='wrapper',children=[
        html.Header(className='main-header',children=[
            html.A(className='logo',children=[
                html.B(children='Orbital Congestion')
            ]),
            html.Nav(className='navbar navbar-static-top',role='navigation', children=[
                html.A(className='sidebar-toggle', role="button", **{'data-toggle':'offcanvas'}, 
                       children=[
                    html.Span(className='sr-only',children='Toggle navigation')
                ])
            ])
        ]),
        html.Aside(className='main-sidebar',children=[
            html.Section(className='sidebar',children=[
                html.Div(className='user-panel', children=[
                    html.Div(className='pull-left image',children=[
                        html.Img(className='img-circle',src='./assets/hat.png')
                    ]),
                    html.Div(className='pull-left info',children='MADS Hatters')
                ]),
                html.Ul(className='sidebar-menu',children=[
                    html.Li(className='header', children='MAIN NAVIGATION'),
                    html.Li(children=[
                        dcc.Tabs(id="menu-tabs", vertical=True,
                                 parent_style={'float': 'left'},
                                 value='menu-item-home',
                                 className="treeview-menu",
                                 style=menu_tabs_styles,
                                 children=[
                            dcc.Tab(label='Home',
                                    value='menu-item-home',
                                    style=menu_tab_style,
                                    selected_style=menu_tab_selected_style),
                            dcc.Tab(label='All Satellites',
                                    value='menu-item-allsats',
                                    style=menu_tab_style,
                                    selected_style=menu_tab_selected_style),
                            dcc.Tab(label='History',
                                    value='menu-item-history',
                                    style=menu_tab_style,
                                    selected_style=menu_tab_selected_style),
                            dcc.Tab(label='Intercepts',
                                    value='menu-item-intercepts',
                                    style=menu_tab_style,
                                    selected_style=menu_tab_selected_style),
                            dcc.Tab(label='Starlink',
                                   value='menu-item-starlink',
                                   style=menu_tab_style,
                                   selected_style=menu_tab_selected_style),
                            dcc.Tab(label='Maneuver Detection',
                                   value='menu-item-maneuvers',
                                   style=menu_tab_style,
                                   selected_style=menu_tab_selected_style),
                            dcc.Tab(label='Gabbard Diagram',
                                    value='menu-item-gabbard',
                                    style=menu_tab_style,
                                    selected_style=menu_tab_selected_style),
                        ]),
                        html.Div(id='ui_dummy', style={'display': 'none'}),
                        html.Div(id='csk', style={'display': 'none'}, children="ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnFkR2tpT2lJd05tSXdORGN5WkMwNE5tUTBMVFExTnpRdFltVTNOeTAxWVRabFpUVTRNRFUzWkRVaUxDSnBaQ0k2TkRBeE5ESXNJbWxoZENJNk1UWXdPRE0xTkRZNE9IMC5uT1pBQ291ay0tZnhQX2V1cXRnRmt3d05TMi02NEJaODFBTWVNbzlwZ1lj")
                    ])
                ])
            ])
        ]),
        html.Div(id='page-content', className='content-wrapper')
    ])
])

# Handle menu selections
@app.callback(
    Output('page-content', 'children'),
    Input('menu-tabs', 'value'))
def render_content(menu_item):
    if menu_item == 'menu-item-home':
        return tab_home.get_page_content()
    elif menu_item == 'menu-item-intercepts':
        return tab_intercept.get_page_content()
    elif menu_item == 'menu-item-history':
        return tab_history.get_page_content()
    elif menu_item == 'menu-item-starlink':
        return tab_starlink.get_page_content()
    elif menu_item == 'menu-item-allsats':
        return tab_allsats.get_page_content()
    elif menu_item == 'menu-item-maneuvers':
        return tab_maneuvers.get_page_content()
    elif menu_item == 'menu-item-gabbard':
        return tab_gabbard.get_page_content()

# Handle maneuver image selection
@app.callback(
    Output('tab-content', 'children'),
    Input('maneuver-tabs', 'value'))
def render_content(tab):
    return tab_maneuvers.get_tab_content(tab)

# Handle allsats settings
@app.callback(
    Output('allsat-table-load','children'),
    Output('allsat-pie-chart','children'),
    Input('dd-allsat-colorby', 'value'))
def update_allsat_settings(color_by):
    return tab_allsats.generate_group_table(color_by)
    
# Handle allsats table changes
@app.callback(
    Output('allsat-graph-load', 'children'),
    Input('dd-allsat-colorby', 'value'),
    Input('allsat-colorseed', 'value'),
    Input('allsat-table-filter', 'derived_virtual_data'),
    Input('allsat-table-filter', 'derived_virtual_selected_rows'))
def update_allsat_display(color_by, color_seed, rows, indexes):
    return tab_allsats.generate_all_sats(color_by, color_seed, rows, indexes)

# Handle allsats select buttons
@app.callback(
    [Output('allsat-table-filter', 'selected_rows'),],
    [Input('satall-selall', 'n_clicks'),
    Input('satall-desall', 'n_clicks')],
    [State('allsat-table-filter', 'derived_virtual_data'),]
)
def update_allsat_selection(selbtn, deselbtn, selected_rows):
    return tab_allsats.select_deselect(selbtn, deselbtn, selected_rows)
    
# Handle intercept filter criteria changes
@app.callback(
    Output('intercept-table', 'data'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('max-prob-slider', 'value'),
    Input('min-dist-slider', 'value'),
    Input('satellite-name', 'value'))
def update_table(start_date, end_date, max_prob, min_dist, sat_name):
    return tab_intercept.generate_intercept_table(start_date, end_date, max_prob, min_dist, sat_name)

# Handle intercept table changes
@app.callback(
    Output('czml', 'children'),
    Input('intercept-table', "derived_virtual_data"),
    Input('intercept-table', "derived_virtual_selected_rows"))
def update_display(rows, derived_virtual_selected_rows):
    return tab_intercept.generate_intercept_czml(rows,derived_virtual_selected_rows)

# Handle starlink show orbit path switch
@app.callback(
    Output('czml2', 'children'),
    Input('show-orbit-path', 'on'))
def update_satellite_filter(show_path):
    return tab_starlink.generate_starlink_czml(show_path)

# Draw and Update Cesium Object on Intercept Menu
app.clientside_callback('''
function(id, czml, menu_item, apikey) {
    // Changed menu - rebuild the viewer
    if (menu_item != window.prev_menu) {
        window.viewer = ''
    }

    // Create the Cesium Viewer
    if (!window.viewer && menu_item == 'menu-item-intercepts') {
        Cesium.Ion.defaultAccessToken = atob(apikey);
        window.viewer = new Cesium.Viewer(id,{
            shouldAnimate: true,
        });
        window.viewer.scene.globe.enableLighting = true;
    }

    // Update the Cesium Viewer
    if (czml && menu_item == 'menu-item-intercepts') {
        window.viewer.dataSources.removeAll();
        czmlJson = JSON.parse(czml);
        window.viewer.dataSources.add(
            Cesium.CzmlDataSource.load(czmlJson)
        );
    }
    window.prev_menu = menu_item

    return true;
}''',
    Output('cesiumContainer', 'data-done'),
    Input('cesiumContainer', 'id'),
    Input('czml', 'children'),
    Input('menu-tabs', 'value'),
    Input('csk', 'children')
)

# Draw and Update Cesium Object on Starlink Menu
app.clientside_callback('''
function(id, czml, menu_item, apikey) {
    // Changed menu - rebuild the viewer
    if (menu_item != window.prev_menu) {
        window.viewer = ''
    }

    // Create the Cesium Viewer
    if (!window.viewer && menu_item == 'menu-item-starlink') {
        Cesium.Ion.defaultAccessToken = atob(apikey);
        window.viewer = new Cesium.Viewer(id,{
            shouldAnimate: true,
        });
        window.viewer.scene.globe.enableLighting = true;
    }

    // Update the Cesium Viewer
    if (czml && menu_item == 'menu-item-starlink') {
        window.viewer.dataSources.removeAll();
        czmlJson = JSON.parse(czml);
        window.viewer.dataSources.add(
            Cesium.CzmlDataSource.load(czmlJson)
        );
    }
    window.prev_menu = menu_item

    return true;
}''',
    Output('cesiumContainer2', 'data-done'),
    Input('cesiumContainer2', 'id'),
    Input('czml2', 'children'),
    Input('menu-tabs', 'value'),
    Input('csk', 'children')
)

# Enable UI Functionality
app.clientside_callback('''
function (data) {
  //Easy access to options
  var o = $.AdminLTE.options;
  
  //Activate sidebar push menu
  if (o.sidebarPushMenu) {
    $.AdminLTE.pushMenu(o.sidebarToggleSelector);
  }

  //Activate box minimize widget
  if (o.enableBoxWidget) {
    $.AdminLTE.boxWidget.activate();
  }

}''',
    Output('ui_dummy','data-done'),
    Input('page-content', 'children')
)

# Suppress errors caused by tabs
app.config['suppress_callback_exceptions'] = True

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
