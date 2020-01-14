import pandas as pd
import numpy as np
import dash
import random as rnd
import urllib.request, json 
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from os import listdir, path, mkdir
from os.path import isfile, join


# ------------------------- CO2 VS DATA ---------------------------------------

class CO2Emissions():

    def __init__(self):
        pass

    
    def get_data(self):
        """ Get the data """

        # Read CDP Data
        co2=pd.read_csv('./data/CO2/CO2_GDP.csv', index_col='Code')
        countries=px.data.gapminder()[['continent', 'iso_alpha']].drop_duplicates()
        countries.columns=['C', 'Code']
        countries=countries.set_index('Code')
        co2=pd.merge(co2, countries, left_index=True, right_index=True)

        # Read Energy Data
        energy=pd.read_csv('./data/CO2/Energy.csv')
        energy=energy[['Code', 'Year', 'Energy_use']]
        co2=pd.merge(co2, energy, how='left', left_on=['Year','Code'], right_on = ['Year','Code'])
        co2['Energy_use'].fillna(0, inplace=True)
        co2=co2[co2['Year']>1950]

        # Meat consumption
        meat_cons=pd.read_csv('./data/CO2/Meat_cons.csv')
        meat_cons=meat_cons[['Code', 'Year', 'Meat_cons']]
        co2=pd.merge(co2, meat_cons, how='left', left_on=['Year','Code'], right_on = ['Year','Code'])

        # Meat Production
        meat_prod=pd.read_csv('./data/CO2/Meat_prod.csv')
        meat_prod=meat_prod[['Code', 'Year', 'Meat_prod']]
        co2=pd.merge(co2, meat_prod, how='left', left_on=['Year','Code'], right_on = ['Year','Code'])

        co2['Meat_cons'].fillna(0, inplace=True)  
        co2['Meat_prod'].fillna(0, inplace=True) 
        co2['CO2_per_capita'].fillna(0, inplace=True)
        co2['GDP_per_capita'].fillna(0, inplace=True)
        co2['Total_population'].fillna(0, inplace=True)
        co2['Energy_use'].fillna(0, inplace=True)

        return co2

    def create_plot(self, data, data_attr = "GDP"):
        """ Create scatter plot"""

        co2 = data

        if data_attr == 'GDP':
            data_x   = "GDP_per_capita"
            x_label  = "GDP Per Capita"
            log_x_c  = True
        elif data_attr == 'ENRG':
            data_x  = "Energy_use"
            x_label = "Energy use per capita"
            log_x_c  = True
        elif data_attr == 'MT_PROD':
            data_x  = "Meat_prod"
            x_label = "Production of Meat (tonnes)"
            log_x_c  = False
        elif data_attr == 'MT_CONS':
            data_x  = "Meat_cons"
            x_label = "Consumption of Meat per Capita (Kg/Yr)"
            log_x_c  = False
        else:
            data_x  = "GDP_per_capita"
            x_label = "GDP Per Capita"

        print(f"Plotting {x_label}")
    
        # Calculate max and mins 
        min_val_x = np.min(co2[data_x].dropna())
        min_val_x = min_val_x - (min_val_x*0)
        max_val_x = np.max(co2[data_x].dropna())
        max_val_x = max_val_x * 1
        min_year=co2[co2[data_x]!=0]['Year'].dropna().min()
        max_year=co2[co2[data_x]!=0]['Year'].dropna().max()

        if log_x_c==True and min_val_x <= 0:
            min_val_x = 100 

        fig = px.scatter(co2[(co2['Year']>min_year)&(co2['Year']<max_year)].dropna(), y="CO2_per_capita", x=data_x, animation_frame="Year", animation_group="Entity",
                size="Total_population", color="C", hover_name="Entity",
                log_x=log_x_c, size_max=55, range_x=[min_val_x,max_val_x], range_y=[-2,25]) # range_x=[100,100000] [min_val_x, max_val_x]

        fig.update_layout(
            height = 500, 
            width  = 1000,
            xaxis_title=x_label, 
            yaxis_title="CO2 Emisions per Capita",
            legend = go.layout.Legend(
                orientation="h",
                font = dict(
                    family="sans-serif",
                    size=12,
                    color="#333333"
                ),
                x=0.1,
                y=1.2
            ),
            font = dict(
                family="sans-serif",
                size=12,
                color="#333333"
            ),
            paper_bgcolor='rgba(0,0,0,0)'
            #plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


# ------------------------- GLOBAL TEMPERATURE ---------------------------------
class GlobalTemperature:

    def __init__(self, pallete = "default"):
        if pallete == "default":
            self._pallete = {'Anual_Mean' : 'deepskyblue', 'Lowess_Smoothing' : 'dimgray'}
        else:
            self._pallete = pallete
    
    def get_data(self):
        """ Get the data Global Mean Estimates based on Land and Ocean Data from NASA webpage."""
    
        df = pd.read_csv('https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt', sep='\s+', header=None, skiprows=5, names=['Year', 'No_Smoothing', 'Lowess(5)'])
        return df

    def create_plot(self, data):
        """ Create time series plot of global temperature. """

        df = data
        fig = go.Figure()
        fig.add_trace(go.Scatter(
                        x=df.Year,
                        y=df['No_Smoothing'],
                        name="Anual Mean",
                        line_color=self._pallete['Anual_Mean'],
                        opacity=0.8))

        fig.add_trace(go.Scatter(
                        x=df.Year,
                        y=df['Lowess(5)'],
                        name="Lowess Smoothing",
                        line_color=self._pallete['Lowess_Smoothing'],
                        opacity=0.8))

        # Use date string to set xaxis range
        fig.update_layout(
            #title_text="Land-Ocean Temperature Index (C)",
            height = 470, 
            width  = 700,
            xaxis_title="Year",
            xaxis=go.layout.XAxis(
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            ),
            yaxis_title="Temperature Anomaly (°C)",
            legend = go.layout.Legend(
                orientation="h",
                font = dict(
                    family="sans-serif",
                    size=12,
                    color="#333333"
                ),
                x=0.1,
                y=1.2
            ),
            font = dict(
                family="sans-serif",
                size=12,
                color="#333333"
            ),
            paper_bgcolor='rgba(0,0,0,0)'
            #plot_bgcolor='rgba(0,0,0,0)'
        )

        return fig



# ------------------------------- AIR QUALITY -----------------------------------
class AirQuality:

    def __init__(self, pallete = "default"):

        if pallete == "default":
            self._pallete = ["#0D9E6E","#FBDE3B","#FF9E3D","#ff5252","#6E0D9E","#850D2E","#EEEEEE"]
        else:
            self._pallete = pallete

        self._a1i_groups = ["Good", "Moderate", "Unhealthy for Sensitive Group", "Unhealthy", "Very Unhealthy", "Hazardous", "No Status"]
            
    # ------------------------------ Air quiality Data API ----------------------------------------------
    # Source: https://aqicn.org/json-api/doc/
    # Token (private):  a9b5573a7d5ca900bcba88b253cae420d7431196
    # Example: https://api.waqi.info/feed/bogota/?token=a9b5573a7d5ca900bcba88b253cae420d7431196
    # Auto IP Location <here>: https://api.waqi.info/feed/here/?token=a9b5573a7d5ca900bcba88b253cae420d7431196
    # Search: https://api.waqi.info/search/?token=a9b5573a7d5ca900bcba88b253cae420d7431196&keyword=bogota
    # LATLONG: https://api.waqi.info/feed/geo:4.5964;-74.0833/?token=a9b5573a7d5ca900bcba88b253cae420d7431196
    # Parameter --> aqi

    def get_aqi_current_pos(self):
        """ 
        - Get current position AQI data -

        aqi_mean, aqi_status, lat_mean, lon_mean, city_name, aqi_color = get_aqi_current_pos()

        """
        AQI_TOKEN = "a9b5573a7d5ca900bcba88b253cae420d7431196"

        try:
            with urllib.request.urlopen(f"https://api.waqi.info/feed/here/?token={AQI_TOKEN}") as url:
                aqi_data = json.loads(url.read().decode())
                if aqi_data["status"] == 'ok':
                    #print(aqi_data)    
                    aqi = aqi_data["data"]["aqi"]
                    lat = aqi_data["data"]["city"]["geo"][0]
                    lon = aqi_data["data"]["city"]["geo"][1]
                    city_name = aqi_data["data"]["city"]["name"]
                    #print(aqi, lat, lon, city_name)

                    aqi_mean = aqi
                    lat_mean = lat
                    lon_mean = lon
                    aqi_status = self.aqi_status(aqi_mean)
                    aqi_color  = self.aqi_color(aqi_mean)

                    return aqi_mean, aqi_status, lat_mean, lon_mean, city_name, aqi_color
                else:
                    return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
        except:
            return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

    def get_aqi_data_city(self, city):
        """ 
        Function that gets the Air Quality Index (AQI) from AQICN API. 
        Input data:
            - city: Name of the city to search for. 

        Output Data:
            - aqi_mean <Numeric>: Air Quality Index (Mean of all stations that matched the search)
            - aqi_status <String>: Air quality status category. It can be ...
                    RANGE       CATEGORY                        HEX COLOR
                    0 - 50	    Good                            #00C24A                      
                    51 -100	    Moderate                        #16C900
                    101-150	    Unhealthy for Sensitive Group   #7FD000
                    151-200	    Unhealthy                       #D7BE00
                    201-300	    Very Unhealthy                  #DE5500
                    300+   	    Hazardous                       #E5001A
            - lat_mean <Numeric>: Average of Latitud among stations
            - lon_mean <Numeric>: Average of Longitude among stations
        
        Example: 
            aqi_mean, aqi_status, lat_mean, lon_mean = get_aqi_data_city("Bogota")

        """

        AQI_TOKEN = "a9b5573a7d5ca900bcba88b253cae420d7431196"
        city = str(city.replace(" ","%20"))

        try:
            with urllib.request.urlopen(f"https://api.waqi.info/search/?token={AQI_TOKEN}&keyword={city}") as url:
                aqi_data = json.loads(url.read().decode())
                if aqi_data["status"] == 'ok':         

                    aqi_v = []
                    lat_v = []
                    lon_v = []

                    for i in aqi_data["data"]:
                        aqi = i["aqi"]
                        if aqi != "-":
                            lat = i["station"]["geo"][0]
                            lon = i["station"]["geo"][1]
                            aqi_v.append(float(aqi))
                            lat_v.append(float(lat)) 
                            lon_v.append(float(lon))

                    aqi_mean = np.mean(aqi_v)
                    lat_mean = np.mean(lat_v)
                    lon_mean = np.mean(lon_v)
                    aqi_status = self.aqi_status(aqi_mean)

                    return aqi_mean, aqi_status, lat_mean, lon_mean
                else:
                    return np.nan, np.nan, np.nan, np.nan
        except:
            return np.nan, np.nan, np.nan, np.nan

        
    def updateAQIData(self, perc_countries = 0.95):
        """ Update the AQI Data based on the CSV File of Cities """

        log_dir   = f"./data" 
        if not path.exists( log_dir ):
            mkdir( log_dir )

        log_dir   = f"./data/AQI" 
        if not path.exists( log_dir ):
            mkdir( log_dir )

        # Read last CSV Data File
        try:
            cities_df = pd.read_csv("./data/AQI/main_cities.csv", delimiter = ";")
            #cities_df = pd.read_csv("./data/AQI/main_cities_first_res.csv", delimiter = ",")
            print(cities_df)
            #cities_df.drop(columns = ['Unnamed: 0.1','Unnamed: 0.1.1','Unnamed: 0','id'], inplace = True)
            cities_data = cities_df.loc[cities_df["pop_weight"] <= perc_countries] #0.81
            cities      = cities_data["city_ascii"]
            n_cities    = len(cities)
            cities_data["AQI_MEAN"]   = np.nan
            cities_data["AQI_STATUS"] = np.nan

            for i, city in enumerate(cities):
                aqi_mean, aqi_status, lat_mean, lon_mean = self.get_aqi_data_city(city)
                if aqi_mean != np.nan:
                    print(f"{i+1}|{n_cities} - The average AQI of {city} is {aqi_status} ({round(aqi_mean,0)})")
                    cities_data["AQI_MEAN"][i]   = aqi_mean
                    cities_data["AQI_STATUS"][i] = aqi_status
                else:
                    print(f"\nWas not possible to get info for {city}.")

            #pallete = ["#0D9E6E","#FBDE3B","#FF9E3D","#ff5252","#6E0D9E","#850D2E", "#EEEEEE"]
            #a1i_groups = ["Good", "Moderate", "Unhealthy for Sensitive Group", "Unhealthy", "Very Unhealthy", "Hazardous", "No Status"]
            # Assign the color
            cities_data["color"] = [self._pallete[self._a1i_groups.index(i)] for i in cities_data["AQI_STATUS"]]

            # Create label column
            cities_data['text'] = cities_data['city_ascii'] + ' - ' + cities_data['country'] + '<br>Population ' + (cities_data['population']/1e6).astype(str) + '<br>AQI: ' + (round(cities_data['AQI_MEAN'],4)).astype(str)
            
            # Update the CSV
            columns = ['city_ascii', 'lat', 'lng', 'country', 'iso3', 'population','pop_weight', 'AQI_MEAN', 'AQI_STATUS', 'color', 'text']
            cities_data.to_csv("./data/AQI/main_cities_first_res.csv", index=False, columns = columns)

            cities_data.dropna(inplace = True)
            cities_data.sort_values("AQI_MEAN", inplace = True)
            cities_data.reset_index(drop = True)

            return cities_data
        except:
            print("(!) Error getting the data - Function: updateAQIData - Class: AirQuality")
            return []

    def createAQIChart(self, dataAQI, scale = 0.1, justUpdate = False):
        """ Create and return a figure chart to be ploted in dashboard """

        # Check if there is a current lat and lon
        aqi_mean, aqi_status, lat_mean, lon_mean, city_name, color = self.get_aqi_current_pos()
        lat_curr = 0 if lat_mean == np.nan else lat_mean
        lon_curr = -180 if lon_mean == np.nan else lon_mean
        print(lat_curr, lon_curr)

        # ---------------------- Create & Update the dash app --------------------
        #scale = 0.1
        # Get current time
        curr_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Create the plot
        fig = go.Figure()
        for grp in self._a1i_groups[:-1]:
            df_sub = dataAQI.loc[dataAQI["AQI_STATUS"]==grp]
            fig.add_trace(go.Scattergeo(
                    #locationmode = 'USA-states',
                    lon  = df_sub['lng'],
                    lat  = df_sub['lat'],
                    text = df_sub['text'],
                    marker = dict(
                        size       = df_sub['AQI_MEAN']/scale,
                        color      = df_sub["color"],
                        line_color = 'rgb(255,255,255)',
                        line_width = 0.5,
                        sizemode   = 'area'
                    )
                    ,name = grp
                )
            )

        fig.update_layout(
            #mapbox= dict(bearing=0, pitch=0, zoom=10, center=dict(lat=xx, lon=yy)),
            showlegend = True,
            height = 400,
            margin=dict(l=0, r=0, t=0, b=0),
            width = 500,
            mapbox_zoom=3,
            mapbox=dict(pitch=0, zoom=-1),
            legend = go.layout.Legend(
                orientation="h",
                font = dict(
                    family="sans-serif",
                    size=12,
                    color="#333333"
                ),
                x=0.1,
                y=1.2
            ),
            font = dict(
                family="sans-serif",
                size=12,
                color="#333333"
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo = dict(
                #scope = 'usa',
                landcolor = '#DACBA0',
                oceancolor = '#344149',
                bgcolor='rgba(0, 0, 0, 0)',
                showframe=False,
                projection = dict(
                    type = 'orthographic',
                    rotation = dict(
                        lon = -50
                    ),
                    scale = 0.85
                ),
                #center_lat=lat_curr,
                #center_lon=lon_curr,
                #projection_rotation_lon=-50,
                showocean = True
            ),
            updatemenus=[dict(type='buttons', 
                                showactive=False,
                                y=1,
                                x=0,
                                xanchor='right',
                                yanchor='top',
                                pad=dict(t=0, r=10),
                                buttons=[dict(label='Play',
                                              method='animate',
                                              args=[None, 
                                                    dict(frame=dict(duration=50, 
                                                                    redraw=True),
                                                         transition=dict(duration=0),
                                                         fromcurrent=True,
                                                         mode='immediate')
                                                   ])
                                        ]
                            )
                        ]
        )

        lon_range = np.arange(-180, 180, 2)

        frames = [dict(traces =[0], #each frame updates the trace 0, i.e. fig.data[0]
                    layout=dict(geo_center_lon=lon,
                                geo_projection_rotation_lon =lon
                                )) for lon in lon_range]

        fig.frames = frames

        print("Map API Updated")
        return fig

    # ================ Auxiliar functions ====================
    def aqi_status(self, aqi_mean):
        aqi_status = "No Status"

        if aqi_mean >= 0 and aqi_mean <= 50:
            aqi_status = "Good"
        elif aqi_mean >= 51 and aqi_mean <= 100:
            aqi_status = "Moderate"
        elif aqi_mean >= 101 and aqi_mean <= 150:
            aqi_status = "Unhealthy for Sensitive Group"
        elif aqi_mean >= 151 and aqi_mean <= 200:
            aqi_status = "Unhealthy"
        elif aqi_mean >= 201 and aqi_mean <= 300:
            aqi_status = "Very Unhealthy"
        elif aqi_mean > 300:
            aqi_status = "Hazardous"
        else:
            aqi_status = "No Status"

        return aqi_status

    def aqi_color(self, aqi_mean):
        aqi_color = self._pallete[-1]

        if aqi_mean >= 0 and aqi_mean <= 50:
            aqi_color = self._pallete[0]
        elif aqi_mean >= 51 and aqi_mean <= 100:
            aqi_color = self._pallete[1]
        elif aqi_mean >= 101 and aqi_mean <= 150:
            aqi_color = self._pallete[2]
        elif aqi_mean >= 151 and aqi_mean <= 200:
            aqi_color = self._pallete[3]
        elif aqi_mean >= 201 and aqi_mean <= 300:
            aqi_color = self._pallete[4]
        elif aqi_mean > 300:
            aqi_color = self._pallete[5]
        else:
            aqi_color = "No Status"

        return aqi_color