from tinytag import TinyTag
import pandas as pd
import tqdm
import os

def get_track_info_from_files(filepath_dict):
    # Loop over them and get details
    records = []
    fails = []
    for directory, files in filepath_dict.items():
        print("\nProcessing tags within files in:\n{}".format(directory))
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
                    'source':path,
                    'bitrate':bitrate,
                    'filetype':filetype,
                    }
                    records.append(d)
                else:
                    # Perhaps audio file was not really an mp3, or is corrupt
                    fails.append({'filename':filename, 'source':path, 'reason':'tag=None', 'filetype':filetype})
            except:
                # Perhaps audio file was not really an mp3, or is corrupt
                fails.append({'filename':filename, 'source':path, 'reason':'audiofile=bad', 'filetype':filetype})

    # Create dataframe
    records = pd.DataFrame().from_dict(records)
    fails = pd.DataFrame().from_dict(fails)
    return records, fails

def clean_string(s):
    s = s.replace('\x00', '')
    return str(s).lstrip().rstrip()

def remove_duplicate_tracks(df):
    # First, sort by bitrate so that when we keep the first, higher quality is kept preferentially
    pre = len(df)
    df = df.sort_values(by='bitrate', ascending=False)
    df['duplicates'] = df.apply(lambda row: '|'.join([str(x).lower() for x in row[['title', 'artist']]]), axis=1)
    df = df.drop_duplicates(subset=['duplicates'], keep='first')
    del df['duplicates']
    print("There were {} duplicates, which have been removed from the record".format(pre-len(df)))
    return df

def validate_artist_names(df, reference_artists=None, blank_name='_Unknown', capitalise_leading_chars=True):
    # Keep note which artists were found in the directory of artists
    ref_artist_match = []
    approved_names = []
    for name in df['artist'].values:
        if reference_artists is None:
            # Incase we don't have a list of names already
            ref_artist_match.append(False)
            approved_names.append(name)
        else:
            name_low = str(name).lower()
            hit_found = False
            for ref_low, ref_normal in zip(reference_artists, reference_artists):
                if hit_found == False:
                    if name_low == ref_low:
                        ref_artist_match.append(True)
                        approved_names.append(ref_normal)
                        hit_found = True
            if hit_found == False:
                ref_artist_match.append(False)
                approved_names.append(name)
    # Add to dataframe
    df['ref_artist_match'] = ref_artist_match
    df['approved_name'] = approved_names
    # Some artists are not found at all, or are completely blank.
    # It would be good to guess artist from the filename. Until then, we shall call them all something else:
    missing_artist_tags = ['', 'no artist', 'unknown artist', 'unknown', 'none', 'artist']
    df['approved_name'] = df['approved_name'].apply(lambda x: blank_name if str(x).lower() in missing_artist_tags else x)
    if capitalise_leading_chars:
        df['approved_name'] = df['approved_name'].apply(lambda x: x[0].upper()+x[1:])
    #print("There are {} confirmed artists with a total of {} tracks".format(len(df[df['ref_artist_match']==True]['artist'].unique()),
    #                                                                        len(df[df['ref_artist_match']==True])))
    return df


def custom_tag_music(df, keywords, searchfields, tagname='custom_tag', case_sensitive=True):
    # Given a list of keywords, and a selection of fields, tag true/false if a keyword is present
    # For example, one may wish to tag xmas songs and store them in a separate directory
    if not case_sensitive:
        keywords = [str(k).lower() for k in keywords]
    keyword_matches = []
    for i in range(len(df)):
        row = df.iloc[i]
        found_match = False
        for c in searchfields:
            s = str(row[c])
            if not case_sensitive:
                s = s.lower()
            for k in keywords:
                if k in s:
                    found_match=True
        keyword_matches.append(found_match)
    df[tagname] = keyword_matches
    return df
