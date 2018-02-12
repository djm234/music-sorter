from IPython import embed

import pandas as pd
import glob
import os
import sys
import tqdm
import shutil
import warnings

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
            try:
                tag = TinyTag.get(path)
                # Extract tag data
                if tag is not None:
                    # Get MetaData
                    artist = clean_string(tag.artist)
                    album = clean_string(tag.album)
                    title = clean_string(tag.title)
                    bitrate = tag.bitrate
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

    # Create dataframe
    records = pd.DataFrame().from_dict(records)
    fails = pd.DataFrame().from_dict(fails)
    return records, fails

def clean_string(s):
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
    df['duplicates'] = df.apply(lambda row: '|'.join([str(x).lower() for x in row[['title', 'artist']]]), axis=1)
    df = df.drop_duplicates(subset=['duplicates'], keep='first')
    del df['duplicates']
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

def copyfile(source, destination):
    # Only perform copy if necessary
    if not os.path.exists(destination):
        shutil.copy2(source, destination)
    return

def sanitise_foldername(s):
    # Strip bad chars for path names
    return ''.join([c for c in s if c not in '?|"<>:;/\\.,*'])


if __name__ == '__main__':
    # Add tqdm to pandas apply functions
    tqdm.tqdm.pandas(desc="Pandas apply progress")

    # Directory to scan
    in_dir = '../mp3/'
    # Directory to copy files to that we process
    out_dir = '../sorted_music/'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Find all .mp3 files in a directory/subdirectories
    filepath_dict = find_files_in_subdirs(in_dir, filetypes=['.mp3', '.wav', '.ogg', '.flac', '.wma', '.mp4', '.m4a'])
    # Process files that are present
    df, fails = get_track_info_from_files(filepath_dict)
    # Remove duplicates found among directories
    df = remove_duplicate_tracks(df)
    # Find out some info
    print("Top 10 artists by track count that were found:\n{}".format(df['artist'].value_counts().head(10)))
    print("The following filetypes were parsed:\n{}".format(df['filetype'].value_counts()))


    # Open a list of artist names we can check against
    reference_artists = pd.read_csv('artist_data/artist_details.csv')
    # See which extracted artists match a reference list
    df = validate_artist_names(df, reference_artists)

    # Some artists are not found at all. Until we can more accurately guess this, filter them out
    df = df[df['approved_name']!='']

    # Save information to file
    df.to_csv(os.path.join(out_dir,'musicFileRecord.csv'))

    include_album_in_path = False

    for i in tqdm.tqdm(range(len(df))):
        row = df.iloc[i]

        # Use the 'approved' name we found earlier
        artist = row['approved_name']
        artist_match = row['artist_match']
        album = row['album']
        title = row['title']
        source = row['filepath']
        fname = os.path.basename(source)

        artist = sanitise_foldername(artist)

        # Append artist name to out directory
        target_dir = os.path.join(out_dir, artist)
        # Add album name, if applicable
        if include_album_in_path:
            if not pd.isnull(album):
                album = sanitise_foldername(album)
                target_dir = os.path.join(target_dir, album)

        # Check if the directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Add filename
        destination = os.path.join(target_dir, fname)

        # Check if file already present
        if not os.path.exists(destination):
            #print("Copying {} to: {}".format(fname, target_dir))
            copyfile(source, destination)



    embed()




    #
