import os
import random
import multiprocessing
import functools
import itertools


import requests
from bs4 import BeautifulSoup

api_key = os.environ.get('LASTFM_API_KEY', None)

def _make_http_request(url, method="get", headers=None, params=None, data=None, auth=None):
    """
    Make an HTTP request and return a json object of the response.
    """
    try:
        request_method = requests.post if method == "post" else requests.get
        res = request_method(url, headers=headers, params=params, data=data, auth=auth)
        responsejson = res.json()

        if res.status_code != 200:
            raise Exception(res.text)
    except ValueError:
        # if the response isn't JSON, .json() method will raise JSONDecodeError,
        # which is a subclass of ValueError
        return res.text
    except Exception as err:
        sys.exit("Error during HTTP request to {}: {}".format(url, err))
    return responsejson


def get_similar_artists(artist, limit=20):
    """
    Returns a list of similar artists to the 'artist'.
    """
    
    params = (('method', 'artist.getsimilar'), ('artist', artist), ('api_key', api_key), ('limit', 100), ('format', 'json'))
    output = _make_http_request("http://ws.audioscrobbler.com/2.0/", params=params)
    artistlist = []
    for artist in output['similarartists']['artist']:
        artistlist.append(artist.get('name', None))
    return random.sample(artistlist, k=limit) if len(artistlist) > limit else artistlist


def get_top_tracks(artist):
    """
    Returns a list of top songs for the 'artist'.
    """

    params = (('method', 'artist.gettoptracks'), ('artist', artist), ('api_key', api_key), ('format', 'json'))
    output = _make_http_request("http://ws.audioscrobbler.com/2.0/", params=params)
    tracklist = []
    for track in output['toptracks']['track']:
        song = track.get('name', None)
        if song is not None:
            tracklist.append("{} - {}".format(song, artist))

    
    return tracklist

def get_youtube_url(query):
    """
    Returns the most relevant youtube link for the query.
    """
    query = query + ", video"    # hint for youtube to only list videos
    res = _make_http_request("https://www.youtube.com/results", "get", params=(('search_query', query),))
    soup = BeautifulSoup(res, "html.parser")
    # we print the first result
    return "https://youtube.com" + soup.find_all(attrs={'class':'yt-uix-tile-link'})[0]['href']

def get_youtube_playlist_slow(seed):
    """
    Return the embed code of the youtube playlist with all the youtube urls given.
    """

    similar_artists = get_similar_artists(seed)
    similar_tracks = [ random.choice(get_top_tracks(artist)) for artist in similar_artists]
    yurls = [get_youtube_url(track) for track in similar_tracks]
    videoids = [url.split("v=")[1] for url in yurls]

    r = requests.get("https://youtube.com/watch_videos?video_ids={vids}".format(vids=','.join(videoids)))
    url = r.url.split("list=")[1]
    return "https://youtube.com/embed/video_series?list={url}&autoplay=1".format(url=url)


def get_youtube_playlist(seed):
    try:
        similar_artists = get_similar_artists(seed)
        pool = multiprocessing.Pool(processes=20)
        top_tracks_similar = [pool.apply_async(get_top_tracks, (x,)) for x in similar_artists]
        similar_tracks = [random.choice(res.get()) for res in top_tracks_similar]

        yurls_pool = [pool.apply_async(get_youtube_url, (x, )) for x in similar_tracks]
        yurls = [res.get() for res in yurls_pool]
        videoids = [url.split("v=")[1] for url in yurls]
        
        r = requests.get("https://youtube.com/watch_videos?video_ids={vids}".format(vids=','.join(videoids)))
        url = r.url.split("list=")[1]
        return "https://youtube.com/embed/video_series?list={url}&autoplay=1".format(url=url)
    except:
        return None

if __name__ == "__main__":
    #print(_make_http_request("http://ws.audioscrobbler.com/2.0/", params=params))
    #print(get_similar_artists('skinshape'))
    print(get_youtube_playlist('modest mouse'))
    #print(get_similar_tracks('skinshape', "I didn't know"))
