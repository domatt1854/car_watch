import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc

from os import listdir
from datetime import timedelta, datetime

import secret

import requests
import re

def capitalize(dealership):
    
    dealership = re.sub("_", " ", dealership)
    dealership = dealership.split(" ")
    
    dealership = [i.capitalize() for i in dealership]
    
    dealership = " ".join(dealership)
    
    return dealership

df = pd.DataFrame()

external_stylesheets = ['https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css']

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


server = app.server


makes = [
    "acura",
    "buick",
    "cadillac",
    "chevrolet",
    "chrysler",
    "gmc",
    "ford",
    "honda",
    "infiniti",
    "jeep",
    "kia",
    "mitsubishi",
    "nissan",
    "porsche",
    "ram",
    "subaru",
    "toyota",
    "volkswagen",
    "volvo",
    "alfa_romeo",
    "rolls_royce",
    "mini",
    "fiat",
    "aston_martin",
    "maserati",
    "bmw",
    "mercedes_benz"
]

capitalized_makes = [capitalize(i) for i in makes]

make_dropdown_to_param = {k: v for k, v in zip(capitalized_makes, makes)}


# capitalized_makes = [
#     "Acura",
#     "Buick",
#     "Cadillac",
#     "Chevrolet",
#     "Chrysler",
#     "GMC",
#     "Ford",
#     "Honda",
#     "Infiniti",
#     "Jeep",
#     "Kia",
#     "Mitsubishi",
#     "Nissan",
#     "Porsche",
#     "Ram",
#     "Subaru",
#     "Toyota",
#     "Volkswagen",
#     "Volvo",
#     "Alfa Romeo",
#     "Rolls Royce",
#     "Mini",
#     "Fiat",
#     "Aston Martin",
#     "Maserati",
#     "Bmw",
#     "Mercedes Benz"
# ]

app.layout = html.Div([
    
    html.H1(
        'Car Watch! Used Car Trends', style= {'text-align': 'center'}
    ),
    
    dcc.Dropdown(
        capitalized_makes,
        'Acura',
        id ='dropdown_make'),
    html.Div(id='display-value'),
    
    dcc.Graph(id='listings_graph', figure={}),
    
    dcc.Graph(id='make_table', figure={})
])

@app.callback(
                Output('display-value', 'children'),
                [Input('dropdown_make', 'value')]
)
def display_value(value):
    return f'You have selected {value}'


@app.callback(
    Output('listings_graph', 'figure'),
    Input('dropdown_make', 'value')
)
def get_recent_week_listings(make: str):

    # grabbing the lower case name of the make
    # this is due to the fact of how the API works
    # Ex: Mercedes Benz -> mercedez_benz   
    make = make_dropdown_to_param[make]

    payload = ""
    headers = {"x-api-key": secret.API_KEY}
    
    
    NUM_DAYS_IN_WEEK = 7

    # to hold the results of all queries of a particular make
    df = pd.DataFrame()
    
    
    for i in range(NUM_DAYS_IN_WEEK):
        
        day = (datetime.now() - timedelta(days=i)).date().isoformat()
    
        querystring = {"make":make,"date":day}

        response = requests.request("GET", secret.API_URL, data=payload, headers=headers, params=querystring)

        df_temp = pd.read_json(response.text)
        df = pd.concat([df, df_temp])
    
    # Need to sort the year later in the Mileage x Price scatter plot
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Year'].astype(str)


    fig = px.scatter(
                    df.sort_values(by='Year'),
                    x = "Mileage",
                    y = "Price",
                    color = "Year",
                    hover_data=["Name"])

    return fig

# @app.callback(
#     Output('make_table', 'figure'),
#     Input('listings_graph', 'figure')
# )
# def create_table():
    


if __name__ == '__main__':
    app.run_server(debug=True)
