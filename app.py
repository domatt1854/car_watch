import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
# pip install dash (version 2.0.0 or higher)
from dash import Dash, dash_table, dcc, html, Input, Output
import dash_bootstrap_components as dbc

from os import listdir
from datetime import timedelta, datetime

import secret

import requests
import re


'''
Connects with the API to pull down the most recent weekly listings
'''


def query_make(make):

    payload = ""
    headers = {"x-api-key": secret.API_KEY}

    NUM_DAYS_IN_WEEK = 7

    # to hold the results of all queries of a particular make
    global df
    
    df = pd.DataFrame()

    for i in range(NUM_DAYS_IN_WEEK):

        day = (datetime.now() - timedelta(days=i)).date().isoformat()

        querystring = {"make": make, "date": day}

        response = requests.request(
            "GET", secret.API_URL, data=payload, headers=headers, params=querystring)

        df_temp = pd.read_json(response.text)
        df = pd.concat([df, df_temp], ignore_index=True)

    # Need to sort the year later in the Mileage x Price scatter plot
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['Year'] = df['Year'].astype(str)

    df.rename(columns={"Name": "Full Model Name"}, inplace=True)

    df = df.sort_values(by='Date')

    return df


app = Dash(
    __name__,
    # suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.CYBORG]
)

curr_make = ''


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


capitalized_makes = [
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
    "BMW",
    "Mercedes Benz"
]


make_dropdown_to_param = {k: v for k, v in zip(capitalized_makes, makes)}

PAGE_SIZE = 15

app.layout = dbc.Container([

    # Top row of text, including title and quick summary of app
    dbc.Row([
        html.H1(
            'Car Watch! Used Car Trends', style={'text-align': 'center'}
        ),
        html.P(
            'Car Watch is tracking thousands of used car listings weekly. Conveniently and easily explore which car models are being sold currently.',
            style={'text-align': 'center'}
        )
    ]),

    # This row includes the components that filter data, and a scatterplot of car listings
    dbc.Row([
        # Left Column, includes:
            # Drop-down menu
            # Filter search bar
            # TODO:
            # slider bar for price, mileage, and year
            dbc.Col(
                [
                    # Dropdown menu
                    dcc.Dropdown(
                        capitalized_makes,
                        'Acura',
                        id='dropdown_make'),
                    html.Div(id='display-value'),
                    dcc.Input(
                        id="filter_search",
                        type='text',
                        placeholder='Type to Search For a Model',
                        style={
                            'marginTop': '5%',
                            'marginBottom': '5%',
                            'height': '10%',
                            'width': '100%'
                        }
                    ),
                    html.H5(
                        'Adjust Price Range',
                        style={
                            'text-align': 'center',
                            'marginTop': '17%'
                        }
                    ),
                    dcc.Slider(
                        id='price-slider',
                        min=0,
                        max=100000,
                        step=500,
                        marks=None,
                        value=100000,
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.H5(
                        'Adjust Mileage Range',
                        style={
                            'text-align': 'center'
                        }
                    ),
                    dcc.Slider(
                        id='mileage-slider',
                        min=0,
                        max=100000,
                        step=500,
                        marks=None,
                        value=100000,
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ]

            ),
            dbc.Col(
                [
                    dcc.Graph(id='listings_graph', figure={})
                ], width=8
            )
            ]
            ),




    html.Br(id='graph_border_1'),

    dbc.Container([
        dbc.Label('Most Recent Listings:'),
        dash_table.DataTable(
            id='make_table',
            columns=[
                {"name": i, "id": i} for i in ['Full Model Name', 'Date', 'Price', 'Mileage']
            ],
            page_current=0,
            page_size=PAGE_SIZE,
            page_action='custom',
            style_data={
                'color': 'black',
                'backgroundColor': 'white'
            },
            style_header={
                'backgroundColor': 'rgb(210, 210, 210)',
                'color': 'black',
                'fontWeight': 'bold'
            }
        )
    ])

    # dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
])


@app.callback(
    Output('display-value', 'children'),
    [Input('dropdown_make', 'value')]
)
def display_value(value):
    return f'You have selected {value}'


# @app.callback(
#     [Output('listings_graph', 'figure'),
#     Output('price-slider', 'min'),
#     Output('price-slider', 'max'),
#     Output('mileage-slider', 'min'),
#     Output('mileage-slider', 'max')],
#     Input('dropdown_make', 'value')
# )
# def get_recent_week_listings(make: str):

#     print('grabbing recent listings')

#     # grabbing the lower case name of the make
#     # this is due to the fact of how the API works
#     # Ex: Mercedes Benz -> mercedez_benz
#     make = make_dropdown_to_param[make]

#     df = query_make(make)

#     fig = px.scatter(
#         df.sort_values(by='Year'),
#         x="Mileage",
#         y="Price",
#         color="Year",
#         hover_data=["Full Model Name"],
#         template='plotly_dark')

#     return fig, df['Price'].min(), df['Price'].max(), df['Mileage'].min(), df['Mileage'].max()


'''
This method is triggered by these interactions:
    - characters are typed into the search bar
    - table is paginated
    
'''


@app.callback(
    [Output('listings_graph', 'figure'),
     Output('make_table', 'data'),
     Output('price-slider', 'min'),
     Output('price-slider', 'max'),
     Output('mileage-slider', 'min'),
     Output('mileage-slider', 'max')],
    [Input('dropdown_make', 'value'),
     Input('filter_search', 'value'),
     Input('price-slider', 'value'),
     Input('mileage-slider', 'value'),
     Input('listings_graph', 'figure'),
     Input('make_table', 'page_current'),
     Input('make_table', 'page_size')])
def update_table(make, search_term, price_slider_value, mileage_slider_value, figure, page_current, page_size):

    global curr_make
    global df
    
    if not make or make != curr_make:
        
        print("Querying new makes... make: {}, previous_make: {}".format(make, curr_make))
        
        param_make = make_dropdown_to_param[make]
        df = query_make(param_make)
        curr_make = make
        
        

    if not search_term:

        temp_df = df[(df['Price'] <= price_slider_value) & (df['Mileage'] <= mileage_slider_value)]

        fig = px.scatter(
            temp_df.sort_values(by='Year'),
            x="Mileage",
            y="Price",
            color="Year",
            hover_data=["Full Model Name"],
            template='plotly_dark')

        return fig, \
               temp_df.iloc[page_current * page_size: (page_current + 1) * page_size].to_dict('records'), \
               df['Price'].min(), \
               df['Price'].max(), \
               df['Mileage'].min(), \
               df['Mileage'].max()

    else:
        
        temp_df = df[(df['Full Model Name'].str.contains(search_term)) & (df['Price'] <= price_slider_value) & (df['Mileage'] <= mileage_slider_value)]

        fig = px.scatter(
            temp_df.sort_values(by='Year'),
            x="Mileage",
            y="Price",
            color="Year",
            hover_data=["Full Model Name"],
            template='plotly_dark')

        return fig, \
               temp_df.iloc[page_current * page_size: (page_current + 1) * page_size].to_dict('records'), \
               df['Price'].min(), \
               df['Price'].max(), \
               df['Mileage'].min(), \
               df['Mileage'].max()

if __name__ == '__main__':
    app.run_server(debug=True)
