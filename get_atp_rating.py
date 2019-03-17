#!/usr/local/bin/python3
import re
import requests
import datetime
import numpy as np
import pandas as pd

# mypy --ignore-missing-imports *.py

if __name__ == "__main__":
    # Get data
    url = "http://tennisabstract.com/reports/atp_elo_ratings.html"
    html = requests.get(url).content
    data = pd.read_html(html)[-1]

    # Extract date
    res = re.search(r'Last update: (.*)</', html.decode())
    date = datetime.datetime.strptime(res.group(1), '%Y-%m-%d') if res else datetime.datetime.today()
    fname = f"elo_{date.year}{date.month:02d}{date.day:02d}.csv"
    
    # Format table
    data = data.iloc[1:]
    data.drop(columns=['Rank', 'Unnamed: 4', 'Unnamed: 8'], inplace=True)
    data.index.name = 'Rank'
    data['Player'] = data['Player'].apply(lambda x: x.replace(u'\xa0', u' '))
    data.replace('-', np.NaN, inplace=True)
    print(data.head(20))

    # Save data
    print('-'*120)
    print(f"Saving file: {fname}")
    print('-'*120)
    data.to_csv(fname)

    # Potential use of data
    surface = 'Hard'
    data_player = data.set_index('Player')
    data_player.loc['Rafael Nadal', surface]
