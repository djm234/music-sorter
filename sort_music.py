from IPython import embed

import pandas as pd
import glob
import os
import sys
import tqdm
import warnings
import string
PRINTABLE = set(string.printable)

import eyed3
from tinytag import TinyTag

def get_track_info_from_files(filepath_dict):
    # Loop over them and get details
    records = []
    fails = []
    for directory, files in filepath_dict.items():
        print("Processing files in: {}".format(directory))
        for filename in tqdm.tqdm(files):
            # Reconstruct path from directory and filename
            path = os.path.join(directory, filename)
            filetype = os.path.splitext(filename)[1].lower()
            #embed()
            #sys.exit()

            # Load mp3
            #audiofile = eyed3.load(path)
            #if audiofile is not None:
            try:
                tag = TinyTag.get(path)
                # Extract tag data
                #tag = audiofile.tag
                if tag is not None:
                    # Get MetaData
                    artist = clean_string(tag.artist)
                    album = clean_string(tag.album)
                    title = clean_string(tag.title)
                    bitrate = tag.bitrate#audiofile.info.mp3_header.bit_rate
                    # Store it
                    d = {
                    'artist':artist,
                    'album':album,
                    'title':title,
                    'filepath':path,
                    'bitrate':bitrate,
                    'filetype':filetype,
                    }
                    records.append(d)
                else:
                    # Perhaps audio file was not really an mp3, or is corrupt
                    fails.append({'filename':filename, 'filepath':path, 'reason':'tag=None', 'filetype':filetype})
            except:
                fails.append({'filename':filename, 'filepath':path, 'reason':'audiofile=bad', 'filetype':filetype})

            #else:
            #    # Perhaps audio file was not really an mp3, or is corrupt
            #    fails.append({'filename':filename, 'path':path, 'reason':'audiofile=None'})
    # Create dataframe
    records = pd.DataFrame().from_dict(records)
    fails = pd.DataFrame().from_dict(fails)
    return records, fails

def clean_string(s):
    #s.decode("utf-8").encode("ascii", "ignore")
    s = s.replace('\x00', '')
    return str(s).lstrip().rstrip()

def find_files_in_subdirs(parent_dir, filetypes=['.mp3']):
    filetypes = [i.lower() for i in filetypes]
    filepath_dict = {}
    filecount = 0
    for root, dirs, files in os.walk(parent_dir):
        if len(files) > 0:
            matching_files = [f for f in files if os.path.splitext(f)[1].lower() in filetypes]
            filepath_dict[root] = matching_files
            filecount += len(matching_files)
    print("There were {} files with extension {} found".format(filecount, filetypes))
    return filepath_dict

def remove_duplicate_tracks(df):
    # First, sort by bitrate so that when we keep the first, higher quality is kept preferentially
    pre = len(df)
    df = df.sort_values(by='bitrate', ascending=False)
    df = df.drop_duplicates(subset=['title'], keep='first')
    print("There were {} duplicates, which have been removed from the record".format(pre-len(df)))
    return df


def validate_artist_names(df, reference_artists):
    # Keep note which artists were found in the directory of artists
    artist_match = []
    approved_names = []
    for name in df['artist'].values:
        name_low = str(name).lower()
        hit_found = False
        for ref_low, ref_normal in zip(reference_artists['name_lowercase'].values, reference_artists['name'].values):
            if hit_found == False:
                if name_low == ref_low:
                    artist_match.append(True)
                    approved_names.append(ref_normal)
                    hit_found = True
        if hit_found == False:
            artist_match.append(False)
            approved_names.append(name)

    df['artist_match'] = artist_match
    df['approved_name'] = approved_names
    print("There are {} confirmed artists with a total of {} tracks".format(len(df[df['artist_match']==True]['artist'].unique()),
                                                                            len(df[df['artist_match']==True])))
    return df


if __name__ == '__main__':
    # Disable warnings about dodgy files highlighted by eyeD3 - only keep errors
    #eyed3.log.setLevel("ERROR")

    # Add tqdm to pandas apply functions
    tqdm.tqdm.pandas(desc="Pandas apply progress")

    # Directory to scan
    in_dir = '../mp3/'
    # Directory to copy files to, provided that we know enough information
    out_dir = '../'

    #if not os.path.exists('mp3record.csv'):
    # Find all .mp3 files in a directory/subdirectories
    filepath_dict = find_files_in_subdirs(in_dir, filetypes=['.mp3', '.wav', '.ogg', '.flac', '.wma', '.mp4', '.m4a'])
    # Process files that are present
    df, fails = get_track_info_from_files(filepath_dict)
    # Remove duplicates found among directories
    df = remove_duplicate_tracks(df)
    # Find out some info
    print("Top 10 artists by track count that were found:\n{}".format(df['artist'].value_counts().head(10)))
    print("The following filetypes were parsed:\n{}".format(df['filetype'].value_counts()))
    # Save to file
    #else:
    #    df = pd.read_csv('mp3record.csv')

    # Open a list of artist names we can check against
    reference_artists = pd.read_csv('artist_details.csv')

    # See which extracted artists match a reference list
    df = validate_artist_names(df, reference_artists)
    # Save to file
    df.to_csv('mp3record.csv')
    # For the artists that did not match, try to make a best guess

    embed()




        #
