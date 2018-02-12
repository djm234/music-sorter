import numpy as np
import pandas as pd
import urllib.request
import os

def get_url_content(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    return text

if __name__ == '__main__':
    # Grab some artist data from the following repo; https://gist.github.com/mbejda
    artist_files = {
    "page1.csv":"https://gist.github.com/mbejda/9912f7a366c62c1f296c/raw/dd94a25492b3062f4ca0dc2bb2cdf23fec0896ea/10000-MTV-Music-Artists-page-1.csv",
    "page2.csv":"https://gist.github.com/mbejda/9912f7a366c62c1f296c/raw/dd94a25492b3062f4ca0dc2bb2cdf23fec0896ea/10000-MTV-Music-Artists-page-2.csv",
    "page3.csv":"https://gist.github.com/mbejda/9912f7a366c62c1f296c/raw/dd94a25492b3062f4ca0dc2bb2cdf23fec0896ea/10000-MTV-Music-Artists-page-3.csv",
    "page4.csv":"https://gist.github.com/mbejda/9912f7a366c62c1f296c/raw/dd94a25492b3062f4ca0dc2bb2cdf23fec0896ea/10000-MTV-Music-Artists-page-4.csv",
    }

    data_dir = 'artist_data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Iterate over files and download locally
    for name, url in artist_files.items():
        if not os.path.exists(name):
            print("Downloading {} from {}".format(name, url))
            with open(os.path.join(data_dir,name), 'w') as f_out:
                content = get_url_content(url)
                f_out.write(content)

    # Re-load them into one big file
    for i, (name, url) in enumerate(artist_files.items()):
        if i == 0:
            df = pd.read_csv(os.path.join(data_dir,name))
        else:
            _df = pd.read_csv(os.path.join(data_dir,name))
            assert np.array_equal(_df.columns.values, df.columns.values), "columns to not match"
            df = df.append(_df)

    # Remove nulls
    df = df[~pd.isnull(df['name'])]
    # Strip whitespace before/after each name
    df['name'] = df['name'].apply(lambda x: str(x).lstrip().rstrip())
    # Make all lowercase for easy lookup, and make note of length to speed matching missing names later
    df['name_lowercase'] = df['name'].apply(lambda x: str(x).lower())
    df['name_length'] = df['name'].apply(lambda x: len(str(x)))

    # Dump to file for later
    df.to_csv(os.path.join(data_dir,'artist_details.csv'))
