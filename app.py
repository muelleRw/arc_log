import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dcc

import plotly.graph_objects as go
import plotly.express as px
from parse_logs import hourly_logs#, parse_logs
from rest_logs import get_token, get_logs
import pandas as pd
import os

#docker build -t arc_logs .

token = get_token()
logs = get_logs(token, "SEVERE", server="REST")

df = pd.DataFrame(logs['logMessages'])
df['time'] = pd.to_datetime(df['time'], unit='ms', origin='unix').dt.tz_localize('UTC').dt.tz_convert(os.getenv('timezone'))
df_hourly = hourly_logs(df)

source = list(set(df_hourly['source']))
source.insert(0,"All")
source_labels = [{'label': x, 'value': x} for x in source]

error_types = list(set(df_hourly['type']))
type_labels = [{'label': x, 'value': x} for x in error_types]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    
        dbc.Row([
            dbc.Col(html.Div([html.Label("Source"), dcc.Dropdown(id='dropdown-source', options=source_labels, value="All")])),
            dbc.Col(html.Div([html.Label("Type"), dcc.Dropdown(id='dropdown-type', options=type_labels, value="SEVERE")])),
        ]),
        dcc.Loading(
            id="loading-2",
            children=[
            dbc.Row([dbc.Col(html.Div(dcc.Graph(id='chart-heat')))]),
            dbc.Row([dbc.Col(html.Div(dcc.Graph(id='chart-time')))]),
            ],
        type="circle",
    )
])



@app.callback(
    [
        Output('chart-heat', 'figure'),
        Output('chart-time', 'figure'),
        
    ], 
    
    [
        Input('dropdown-source', 'value'),
        Input('dropdown-type', 'value')
    ]
)
def update_figures(source, type):#need to make this check if outage is in db
    if source != "All":
        df_hourly_filtered = df_hourly[df_hourly['source'] == source]
    else:
        df_hourly_filtered = df_hourly.groupby(['date', 'type'])['errors'].sum().reset_index()
        df_hourly_filtered.columns = ['date', 'type', 'errors']
        df_hourly_filtered['source'] = source
    
    by_hour = df_hourly_filtered[df_hourly['type'] == type]
    by_hour = pd.DataFrame(pd.date_range(by_hour['date'].min(),by_hour['date'].max(),freq='H'),columns= ['date']).merge(by_hour,on=['date'],how='outer').fillna(0)
    by_hour.loc[by_hour['source'] == 0,"source"] = source

    by_hour['time'] = by_hour['date'].dt.time
    by_hour['day'] = by_hour['date'].dt.date
    by_hour.sort_values('time', inplace=True)

    heat_fig = go.Figure(
        data=go.Heatmap(
            z=by_hour["errors"], y=by_hour["day"], x=by_hour["time"], 
            zauto=False, zmax= by_hour['errors'].quantile(0.99)
        ),
        layout=go.Layout(title="ArcGIS Rest Errors (Source Only)", template="simple_white")
    )

    time_fig = px.scatter(df_hourly_filtered, x='date', y='errors', color='source', title="All Rest Errors by Source",  template="simple_white")
    return [heat_fig, time_fig]

if __name__ == '__main__':
    app.run_server(debug=True)