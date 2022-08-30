import pandas as pd
import plotly.express as px  
import plotly.graph_objects as go
from dash import Dash, dash_table, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import timedelta, datetime
import secret
import requests
import makes
import re

# How many rows will display on the data table
PAGE_SIZE = 14

# Used for determining when new data needs to be pulled down
curr_make = ''

# csv containing up-to-date car models to categorize car listings
df_makes_models = pd.read_csv('data/makes_models.csv')

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG]
)

application = app.server


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
            dbc.Col(
                [
                    # Dropdown menu
                    dcc.Dropdown(
                        makes.DROP_DOWN_MENU_MAKES,
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
                    # Sliders
                    html.H5(
                        'Adjust Price Range',
                        style={
                            'text-align': 'center',
                            'marginTop': '10%'
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
            # Scatterplot
            dbc.Col(
                [
                    dcc.Graph(id='listings_graph', figure={})
                ], width=8
            )
            ]
            ),

    html.Br(id='graph_border_1'),

    # data table and horizontal bar chart
    dbc.Row([
        dbc.Col(
            [dbc.Label('Most Popular Car Models Listed for Sale'),
             dcc.Graph(id='horizontal_bar_car_models', figure={})],
            width=6
        ),
        dbc.Col(
            [dbc.Label('Most Recent Listings:'),
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
            )],
            width=6
        )
    ])

])


def string_together_amg(name):
    if name:
        name = re.sub('Benz AMG', 'Benz-AMG', name)
    return name


'''
this method joins together the car listing data to a separate data set that contains the specific model type
'''


def partial_match(name, models):

    for i in models:

        lower = i.lower()

        # checking for substring matches
        if lower in name.lower():
            return i

        # matching BMW's
        elif 'bmw' in lower:
            res = re.search(r"(\d{3})", name)
            if res:
                return "{} Series".format(res.group(1)[0])

    return 'Other'


'''
Connects with the API to pull down the most recent weekly listings.
'''


def query_make(make):

    global df
    global df_makes_models

    payload = ""
    headers = {"x-api-key": secret.API_KEY}
    NUM_DAYS_IN_WEEK = 7

    # to hold the results of all queries of a particular make
    df = pd.DataFrame()

    # this filter makes it so that there is less computation involved to find the partial matches of each car model
    filter_makes_models = df_makes_models[df_makes_models['Make']
                                          == makes.MAKES_DROPDOWN_TO_JOIN_KEY[make]]['Model']
    filter_makes_models = filter_makes_models.unique().tolist()

    if makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Ram':
        filter_makes_models.extend(makes.RAM_MODELS)

    elif makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Rolls Royce':
        filter_makes_models.extend(makes.ROLLS_ROYCE_MODELS)

    elif makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Aston Martin':
        filter_makes_models.extend(makes.ASTON_MARTIN_MODELS)

    elif makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Nissan':
        filter_makes_models.extend(makes.NISSAN_MODELS)

    elif makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Toyota':
        filter_makes_models.extend(makes.TOYOTA_MODELS)

    elif makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Gmc':
        filter_makes_models.extend(makes.GMC_MODELS)

    elif makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Chevrolet':
        filter_makes_models.extend(makes.CHEVY_MODELS)

    elif makes.MAKES_DROPDOWN_TO_JOIN_KEY[make] == 'Ford':
        filter_makes_models.extend(makes.FORD_MODELS)

    # Query the most recent listings since last week
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

    # partial match
    df['Full Model Name'] = df['Full Model Name'].apply(
        lambda x: string_together_amg(x))
    df['Make-Model'] = df['Full Model Name'].apply(
        lambda x: partial_match(x, filter_makes_models))

    return df


'''
This method updates the row of text under the drop-down mneu
'''
@app.callback(
    Output('display-value', 'children'),
    [Input('dropdown_make', 'value')]
)
def display_value(value):
    return f'You have selected {value}'


'''
This method is triggered by just about all forms of interaction in the dashboard.
It handles all figure and data updating
'''
@app.callback(
    [Output('horizontal_bar_car_models', 'figure'),
     Output('listings_graph', 'figure'),
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

    # decides whether or not we need to query new data
    if not make or make != curr_make:

        # converts the uppercase display value of a make to the parameter version
        # Mercedez Benz -> mercedez_benz
        param_make = makes.MAKES_DROPDOWN_TO_PARAMETER_QUERY[make]

        # fetch the query results
        df = query_make(param_make)
        curr_make = make

    # if the search bar is empty
    if not search_term:

        temp_df = df[(df['Price'] <= price_slider_value) &
                     (df['Mileage'] <= mileage_slider_value)]

        data_bar = pd.DataFrame(temp_df['Make-Model'].value_counts())
        data_bar = data_bar.rename(columns={'Make-Model': 'Count'})
        data_bar.index.names = ['Model']

        fig_bar = px.bar(data_bar, x='Count',
                         y=data_bar.index, orientation='h')

        fig_bar.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                              marker_line_width=1.5, opacity=0.6)

        fig_scatter = px.scatter(
            temp_df.sort_values(by='Year'),
            x="Mileage",
            y="Price",
            color="Year",
            hover_data=["Full Model Name"],
            template='plotly_dark')

        return fig_bar, \
            fig_scatter, \
            temp_df.iloc[page_current * page_size: (page_current + 1) * page_size].to_dict('records'), \
            df['Price'].min(), \
            df['Price'].max(), \
            df['Mileage'].min(), \
            df['Mileage'].max()

    # the user wants to search for a particular model
    else:

        temp_df = df[(df['Full Model Name'].str.contains(search_term)) & (
            df['Price'] <= price_slider_value) & (df['Mileage'] <= mileage_slider_value)]

        data_bar = pd.DataFrame(temp_df['Make-Model'].value_counts())
        data_bar = data_bar.rename(columns={'Make-Model': 'Count'})
        data_bar.index.names = ['Model']

        fig_bar = px.bar(data_bar, x='Count',
                         y=data_bar.index, orientation='h')
        
        fig_bar.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                        marker_line_width=1.5, opacity=0.6)

        fig_scatter = px.scatter(
            temp_df.sort_values(by='Year'),
            x="Mileage",
            y="Price",
            color="Year",
            hover_data=["Full Model Name"],
            template='plotly_dark')

        return fig_bar, \
            fig_scatter, \
            temp_df.iloc[page_current * page_size: (page_current + 1) * page_size].to_dict('records'), \
            df['Price'].min(), \
            df['Price'].max(), \
            df['Mileage'].min(), \
            df['Mileage'].max()


if __name__ == '__main__':
    app.run_server(debug=True)