import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
from os import listdir
import secret

import requests
import json

external_stylesheets = ['https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css']

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# pulling down latest listings
data_all = []

files = listdir('data')

for i in files:

    if 'png' in i or 'txt' in i:
        continue
    
    file_path = "data/{}".format(i)
    
    df = pd.read_csv(file_path, on_bad_lines = 'skip')
    df['Make'] = i[:-4]
    df = df.drop(columns=["Unnamed: 0"])
    
    data_all.append(df)
    
df = pd.concat(data_all, axis = 0, ignore_index=True)

server = app.server

makes = [
    "Acura",
    "Buick",
    "Cadillac",
    "Chevrolet",
    "Chrysler",
    "GMC",
    "Ford",
    "Honda",
    "Infiniti",
    "Jeep",
    "Kia",
    "Mitsubishi",
    "Nissan",
    "Porsche",
    "Ram",
    "Subaru",
    "Toyota",
    "Volkswagen",
    "Volvo",
    "Alfa Romeo",
    "Rolls Royce",
    "Mini",
    "Fiat",
    "Aston Martin",
    "Maserati",
    "Vmw",
    "Mercedes Benz"
]

app.layout = html.Div([
    html.H1('Car Watch! Used Car Trends'),
    dcc.Dropdown(makes,
        'Acura',
        id='dropdown_make'
    ),
    dcc.Dropdown(makes,
        'Acura',
        id='dropdown_date'
    ),
    html.Div(id='display-value')
])

@app.callback(Output('display-value', 'children'),
                [Input('dropdown_make', 'value')])
def display_value(value):
    return f'You have selected {value}'


def get_daily_make_listings(make, date):
    
    query_parameters = {"make":make,"date":date}
    payload = ""
    headers = {"x-api-key": secret.API_KEY}

    response = requests.request("GET", secret.API_URL, data=payload, headers=headers, params=query_parameters)    

    res = json.loads(response.text)

if __name__ == '__main__':
    app.run_server(debug=True)
