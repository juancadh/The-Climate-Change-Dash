import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import random as rnd
import urllib.request, json 
import time
from datetime import datetime
import plotly.graph_objects as go
from procedures.environment_functions import AirQuality, GlobalTemperature, CO2Emissions, WasteGeneration
from flask import Flask
import plotly.express as px
import os 


# HEROKU APP:  http://the-climate-change-app.herokuapp.com/

# -----------------------------------------------------------------------------------
# ----------------------------- INITIAL DATA ----------------------------------------
# -----------------------------------------------------------------------------------

# ------------------------------WASTE GENERATION ------------------------------------
waste_gen = WasteGeneration()
dataWaste = waste_gen.get_data()
figWaste  = waste_gen.create_plot(dataWaste)

# ----------------------------- CO2 VS DATA -----------------------------------------
co2_emiss = CO2Emissions()
dataCO2   = co2_emiss.get_data()
figCO2    = co2_emiss.create_plot(dataCO2, "GDP")

# ----------------------------- GLOBAL TEMPERATURE ----------------------------------
glob_temp    = GlobalTemperature("default")
dataGlobTemp = glob_temp.get_data()
last_year          = dataGlobTemp["Year"].iloc[-1:].values[0]
last_year_temp_val = dataGlobTemp["No_Smoothing"].iloc[-1:].values[0]
last_year_moved    = 'increased' if last_year_temp_val>0 else 'decreased'
figGlobTemp  = glob_temp.create_plot(dataGlobTemp)

# ----------------------------- AIR QUALITY -----------------------------------------

# Initialize the class of functions
aqi_fun = AirQuality("default")

# Initial Base (the most recent data)
dataAQI = pd.read_csv("./data/AQI/main_cities_first_res.csv", delimiter = ",")
dataAQI.dropna(inplace = True)
dataAQI.sort_values("AQI_MEAN", inplace = True)
dataAQI.reset_index(inplace=True, drop=True)
best         = dataAQI.iloc[0]
worst        = dataAQI.iloc[-1]
best_place   = best["city_ascii"] + ", " + best["country"]
best_aqi     = round(best["AQI_MEAN"], 1)
best_color   = best["color"]
worst_place  = worst["city_ascii"] + ", " + worst["country"]
worst_aqi    = round(worst["AQI_MEAN"], 1)
worst_color  = worst["color"]
time_update  = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Get Current Data
aqi_mean, aqi_status, lat_mean, lon_mean, city_name, color = aqi_fun.get_aqi_current_pos()

if city_name != np.nan:
    city    = city_name.split(",")[0]
    country = city_name.split(",")[-1]
    curr_city    = city + ", " + country
    curr_aqi = aqi_mean
    curr_color = color

# Create the AQI plot fig
AQIfig = aqi_fun.createAQIChart(dataAQI, scale = 0.2)

# -----------------------------------------------------------------------------------
# ---------------------------- CREATE THE APP ---------------------------------------
# -----------------------------------------------------------------------------------
UPDATE_MINS = 30

meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]

#server = Flask(__name__)
#server.secret_key = os.environ.get('secret_key', 'secret')

#app = dash.Dash(__name__, server = server, meta_tags=meta_tags)
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.H1(
        id = "main_title",
        children='The Climate Change App'
    ),

    html.H2(
        className = "subtitle_title",
        children='Raising Earth Consciousness through Data Visualization. This dashboard provides a set of visual tools to keep track of climate change issues and be aware of our footprint and impact on the planet.'
    ),

    html.Div(
        className='data_numbers_container',
        children=[
            html.Div(
                className='data_num_box',
                children=[
                    html.H2(children='Ice Sheets Loss'),
                    html.H3(children='206.5 Gt'),
                    html.H4(children='Gigatones per year since 2002'),
                    html.H6(children='Source: climate.nasa.gov')
                ]
            ),
            html.Div(
                className='data_num_box',
                children=[
                    html.H2(children='Extinctions'),
                    html.H3(children='10 K'),
                    html.H4(children='Species go extinct every year'),
                    html.H6(children='Source: wwf.panda.org')
                ]
            ),
            html.Div(
                className='data_num_box',
                children=[
                    html.H2(children='Fires'),
                    html.H3(children='4.5 M'),
                    html.H4(children='Wildfires worldwide in 2019'),
                    html.H6(children='Source: Global Forest Watch Fires')
                ]
            ),
            html.Div(
                className='data_num_box',
                children=[
                    html.H2(children='See Level'),
                    html.H3(children='96 (±4) mm'),
                    html.H4(children='Has increased since 1993'),
                    html.H6(children='Source: sealevel.nasa.gov')
                ]
            )
        ]
    ),

    # ----- MAIN CONTAINER -----
    html.Div(
        className='main_container',
        children=[

            # -------- FIRST SECTION --------
            html.Div(
                className='section_container',
                children =[

                    # ---- AIR QUALITY BOX -----
                    html.Div(
                        className="box-style",
                        children=html.Div([
                            # Title
                            html.H3('Current Air Quality Index (AQI)'),
                            # Subtitle
                            html.H6('Golbal Air Quality Index by capitals provided by the World Air Quality Index project'),
                            # Data of current position
                            html.Div(
                                id = 'curr_data_api_cont',
                                className = 'curr_data_api_cont',
                                children = [
                                    html.Div([
                                        html.H3(id='current_pos_aqi_val', children=f"{str(curr_aqi)}", style = {'color':curr_color}),
                                        html.H4(id='current_pos_aqi_city_name', children="{}".format(curr_city))
                                    ]),
                                    html.Div([
                                        html.H5("Best"),
                                        html.H3(id='current_pos_aqi_val_best', children=f"{str(best_aqi)}", style = {'color':best_color}),
                                        html.H4(id='current_pos_aqi_city_name_best', children="{}".format(best_place))                        
                                    ]),
                                    html.Div([
                                        html.H5("Worst"),
                                        html.H3(id='current_pos_aqi_val_worst', children="{}".format(worst_aqi), style = {'color':worst_color}),
                                        html.H4(id='current_pos_aqi_city_name_worst', children="{}".format(worst_place))
                                    ])
                                ]
                            ),
                            # AQI Chart
                            html.Div(
                                className = "plot_wrap",
                                children = html.Div([
                                    dcc.Graph(
                                        id='airquality-graph',
                                        figure=AQIfig
                                    ),
                                    dcc.Interval(
                                        id='interval-component',
                                        interval=UPDATE_MINS*60*1000, # in milliseconds
                                        n_intervals=0
                                    )
                                ])
                            ),
                            # Info last update
                            html.P(
                                id='live-update-text',
                                className = "live_update_text",
                                children = "Last update: {} - Source: aqicn.org".format(time_update)
                            )
                        ])
                    )
                ]
            ),

            # -------- SECOND SECTION --------
            html.Div(
                className='section_container',
                children =[
                    # --------- GLOBAL TEMPERATURE -------
                    html.Div(
                        className='box-style',
                        children=html.Div([
                            # Title
                            html.H3('Land-Ocean Temperature Index (°C)'),
                            # Subtitle
                            html.H6('Change in global surface temperature relative to 1951-1980 average temperatures'),
                            # Data of current position
                            html.Div(
                                className = 'global_temp_box_cont',
                                children = [
                                    html.Div([
                                        html.H3(children=f"{last_year_temp_val}°C"),
                                        html.H4(children=f"has {last_year_moved} the global temperature from the 1951 to 1980 mean to {last_year}.")
                                    ])
                                ]
                            ),
                            # AQI Chart
                            html.Div(
                                className = "plot_wrap",
                                children = html.Div([
                                    dcc.Graph(
                                        id='globaltemp-graph',
                                        figure=figGlobTemp
                                    )
                                ])
                            ),
                            # Info last update
                            html.P(
                                className = "live_update_text",
                                children = 'Source: climate.nasa.gov'
                            )
                        ])
                    )
                ]
            ),

            # -------- THIRD SECTION --------
            html.Div(
                className='section_container',
                children =[
                    # --------- CO2 EMISSIONS -------
                    html.Div(
                        className='box-style',
                        children=html.Div([
                            # Title
                            html.H3('CO2 Emissions'),
                            # Subtitle
                            html.H6('Emissions of CO2 per capita. Select an attribute from the following list:'),
                            # Drop down menu
                            dcc.Dropdown(
                                id='co2-dropdown',
                                className='dropdown_class1',
                                options=[
                                    {'label': 'GDP per capita', 'value': 'GDP'},
                                    {'label': 'Energy Consumption per capita', 'value': 'ENRG'},
                                    {'label': 'Consumption of Meat per Capita', 'value': 'MT_CONS'},
                                    {'label': 'Production of Meat', 'value': 'MT_PROD'}
                                ],
                                value='GDP',
                                searchable = False,
                                clearable=False
                            ),                      
                            # AQI Chart
                            html.Div(
                                className = "plot_wrap",
                                children = html.Div([
                                    dcc.Graph(
                                        id='co2emissions-graph',
                                        figure=figCO2
                                    )
                                ])
                            ),
                            # Info last update
                            html.P(
                                className = "live_update_text",
                                children = 'Source: pbl.nl/en  | worldbank | fao.org'
                            )
                        ])
                    )
                ]
            ),

            # -------- FOURTH SECTION --------
            html.Div(
                className='section_container',
                children =[
                    # --------- GENERATION OF WASTE -------
                    html.Div(
                        className='box-style',
                        children=html.Div([
                            # Title
                            html.H3('Generation of Waste'),
                            # Subtitle
                            html.H6('Total amount of waste generated by sector of activity in thousands of tonnes for 2016.'),                     
                            # AQI Chart
                            html.Div(
                                className = "plot_wrap",
                                children = html.Div([
                                    dcc.Graph(
                                        id='wastegen-graph',
                                        figure=figWaste
                                    )
                                ])
                            ),
                            # Info last update
                            html.P(
                                className = "live_update_text",
                                children = 'Source: stats.oecd.org/'
                            )
                        ])
                    )
                ]
            )
        ]
    ),

    html.H3(
        className = "credits",
        children='Developed by Maria F. Restrepo & Juan C. Díaz | DV Final Project | 2020'
    ),
])


# ----------------- DROPDOWN FOR CO2 ---------------------------------
@app.callback(
    Output('co2emissions-graph', 'figure'),
    [Input('co2-dropdown', 'value')])
def update_output(value):
    figCO2    = co2_emiss.create_plot(dataCO2, value)
    return figCO2


# ----------------- UPDATE THE TEXTS EVERY N MINUTES ------------------
@app.callback([Output('current_pos_aqi_val', 'children'), Output('current_pos_aqi_city_name', 'children')],
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    # Get current position data from API Source
    aqi_fun = AirQuality("default")
    aqi_mean, aqi_status, lat_mean, lon_mean, city_name, color = aqi_fun.get_aqi_current_pos()

    if city_name != np.nan:
        city    = city_name.split(",")[0]
        country = city_name.split(",")[-1]
        city = city + ", " + country
    return html.Span(aqi_mean, style = {'color': color}), city


# ----------------- UPDATE THE API CHART EVERY N MINUTES ------------------
@app.callback([Output('airquality-graph', 'figure'), Output('live-update-text', 'children'),
               Output('current_pos_aqi_val_best', 'children'), Output('current_pos_aqi_city_name_best', 'children'),
               Output('current_pos_aqi_val_worst', 'children'), Output('current_pos_aqi_city_name_worst', 'children')],
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    # Get data from the AIP Source to update the values
    dataAQI = aqi_fun.updateAQIData(perc_countries = 0.95)
    # Create the chart figure
    AQIfig  = aqi_fun.createAQIChart(dataAQI, scale = 0.2)

    dataAQI.dropna(inplace = True)
    dataAQI.sort_values("AQI_MEAN", inplace = True)
    dataAQI.reset_index(inplace=True, drop=True)
    best  = dataAQI.iloc[0]
    worst = dataAQI.iloc[-1]
    best_place   = best["city_ascii"] + ", " + best["country"]
    best_aqi     = round(best["AQI_MEAN"],1)
    worst_place = worst["city_ascii"] + ", " + worst["country"]
    worst_aqi     = round(worst["AQI_MEAN"],1)
    #print(best["city_ascii"], best["country"], best["AQI_MEAN"], best["AQI_STATUS"], best["color"])
    #print(worst["city_ascii"], worst["country"], worst["AQI_MEAN"], worst["AQI_STATUS"], worst["color"])

    # Update time
    time_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text_print = f"Last updated: {time_update} - Source: aqicn.org"

    return AQIfig, text_print, html.Span(best_aqi, style = {'color': best["color"]}), best_place, html.Span(worst_aqi, style = {'color': worst["color"]}), worst_place
 


if __name__ == '__main__':
    app.run_server(debug=True)