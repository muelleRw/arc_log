import pathlib
import re
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

bracket_pattern = re.compile(r"\<(.+?)\>")

errors = []
def parse_logs():

    for txt_file in pathlib.Path(os.getenv("log_path")).glob('*.log'):
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
    df = pd.DataFrame(errors)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')
    df = df[~df['type'].isna()]
    
    return df
#df.to_csv("logs.csv", index=False)


def hourly_logs(df):
    df['date_h'] = df['time'].dt.floor('H')
    by_hour = df.groupby(['date_h', 'source', 'type'])['time'].count().reset_index()
    by_hour.columns=["date", "source", "type", "errors"]
    return by_hour
