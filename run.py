import pathlib
import re

bracket_pattern = re.compile(r"\<(.+?)\>")

errors = []

for txt_file in pathlib.Path('\\\\54025GIS/arcgisserver/logs/54025GIS.PRECORP.ORG/server').glob('*.log'):
    print(txt_file)
    with open(txt_file, "r") as f:
        for line in f:
            error_match =  re.search(r"(?<=\>)(.+?)(?=\<)", line)
            details_match = bracket_pattern.match(line)
            
            if not details_match:
                continue
            if error_match is not None:
                error_msg = error_match.group(0)
            else:
                error_msg = None
            details = details_match.group(0)
            details_list = details.split(" ")
            details = {}
            details_list = [x for x in details_list if "=" in x]
            for detail in details_list:
                detail_info = detail.split("=")
                detail_info[1] = detail_info[1].replace('"', '')
                details[detail_info[0]] = detail_info[1]

            details["error"] = error_msg

            errors.append(details)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
df = pd.DataFrame(errors)
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time')
df = df[~df['type'].isna()]
df['date_h'] = df['time'].dt.floor('H')
df.to_csv("logs.csv", index=False)
by_hour = df.groupby(['date_h', 'source'])['time'].count().reset_index()
by_hour.columns=["date", "source", "errors"]
by_hour = by_hour[by_hour['source'] == 'Rest']
by_hour = pd.DataFrame(pd.date_range(by_hour['date'].min(),by_hour['date'].max(),freq='H'),columns= ['date']).merge(by_hour,on=['date'],how='outer').fillna(0)
by_hour.loc[by_hour['source'] == 0,"source"] = "reset"

by_hour['time'] = by_hour['date'].dt.time
by_hour['day'] = by_hour['date'].dt.date
by_hour.sort_values('time', inplace=True)

heat_fig = go.Figure(
    data=go.Heatmap(
        z=by_hour["errors"], y=by_hour["day"], x=by_hour["time"], 
        zauto=False, zmax= by_hour['errors'].quantile(0.99)
    ),
    layout=go.Layout(title="ArcGIS Rest API Errors", template="simple_white")
)
heat_fig.show()

fig = px.scatter(by_hour, x='date', y='errors', color='source')
fig.show()


import logging
logging.basicConfig(filename='test.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
z = 32

logging.warning(str(z))
