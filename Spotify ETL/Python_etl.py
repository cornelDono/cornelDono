import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
import sys

def spotify_etl_func():

    connection = psycopg2.connect(user="postgres",
                                    password="pgpwd4habr",
                                    host="127.0.0.1",
                                    port="5432")

    cur = connection.cursor()
    engine = create_engine('postgresql+psycopg2://postgres:pgpwd4habr@localhost:5432/postgres')
    conn_eng = engine.raw_connection()
    cur_eng = conn_eng.cursor()

    spotify_client_id = "96a5020b4f4443e78037a94150520124"
    spotify_client_secret = "3101254c8d0e413287b42d159393df5a"
    spotify_redirect_url = "http://127.0.0.1:8080/"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id,
                                                    client_secret=spotify_client_secret,
                                                    redirect_uri=spotify_redirect_url,
                                                    scope="user-read-recently-played user-read-private user-top-read user-read-currently-playing"))

    before_last = []
    album_list = []
    song_list= []
    artist_list = []


    cur.execute("SELECT * FROM spotify.index")
    last_song_sql = int(cur.fetchone()[0])
 
    if  not sp.current_user_recently_played(limit=1, after=last_song_sql)['items']:
        print('no new songs')
        return "Finished, No new songs"
    else:
        while sp.current_user_recently_played(limit=1, after=last_song_sql)['items']:
            recently_played = sp.current_user_recently_played(limit=1, after=before_last)
            row = recently_played['items'][0]
            if row['track']['album']['album_type'] != "single":
                album_id = row['track']['album']['id']
                album_name = row['track']['album']['name']
                album_release_date = row['track']['album']['release_date']
                album_total_tracks = row['track']['album']['total_tracks']
                album_url = row['track']['album']['external_urls']['spotify']
                album_element = {'album_id':album_id,'album_name':album_name,'album_release_date':album_release_date,
                                    'album_total_tracks':album_total_tracks,'album_url':album_url}
                album_list.append(album_element)

            artist_id = row['track']['artists'][0]['id']
            artist_name = row['track']['artists'][0]['name']
            song_name = row['track']['name']
            song_popularity = row['track']['popularity']
            song_url= row['track']['external_urls']['spotify']
            duration_ms = row['track']['duration_ms']
            played_at = row['played_at']
            song_element = {'artist_id':artist_id, 'artist_name':artist_name, 'song_name':song_name, 
                                'song_popularity':song_popularity, 'song_url': song_url, 'duration_ms':duration_ms,
                                'played_at':played_at}
            
            song_list.append(song_element)

            artist_link = row['track']['artists'][0]['external_urls']['spotify']
            artist_element = {'artist_id':artist_id, 'artist_name':artist_name, 'artist_link':artist_link}

            artist_list.append(artist_element)



            last_song_sql = int(recently_played['cursors']['after'])
 



        albume_frame = pd.DataFrame(album_list, columns=['album_id','album_name','album_release_date','album_total_tracks','album_url'])
        history_song_frame = pd.DataFrame(song_list, columns=['artist_id', 'artist_name', 'song_name', 'song_popularity', 'song_url', 'duration_ms','played_at'])
        artist_frame = pd.DataFrame(artist_list, columns=['artist_id', 'artist_name', 'artist_link'])
        last_song_frame = pd.DataFrame(last_song_sql)

        albume_frame = albume_frame.drop_duplicates(subset=['album_id'])
        artist_frame = artist_frame.drop_duplicates(subset=['artist_id'])
        history_song_frame['played_at'] = pd.to_datetime(history_song_frame['played_at'], errors='coerce', format='%Y-%m-%dT%H:%M:%S.%fZ')

        print(artist_frame.head(5))
        print(history_song_frame.head(5))
        print(albume_frame.head(5))

        if not albume_frame.empty:
            cur_eng.execute(
                    """
                    CREATE TEMP TABLE IF NOT EXISTS tmp_album AS SELECT * FROM spotify.album_list LIMIT 0
                    """)
            albume_frame.to_sql("tmp_album", con = engine, if_exists='append', index = False)

            cur.execute(
                    """
                    INSERT INTO spotify.album_list
                    SELECT tmp_album.*
                    FROM tmp_album
                    JOIN spotify.album_list on spotify.album_list.album_id = tmp_album.album_id
                    WHERE spotify.album_list.album_id IS NULL;
                    

                    DROP TABLE tmp_album
                    """)
            connection.commit()

        cur_eng.execute(
                """
                CREATE TEMP TABLE IF NOT EXISTS tmp_artist AS SELECT * FROM spotify.artist_list LIMIT 0
                """
        )
        artist_frame.to_sql('tmp_artist', con = engine, if_exists='append', index = False)

        cur.execute(
                """
                INSERT INTO spotify.artist_list
                SELECT tmp_artist.*
                FROM tmp_artist
                JOIN spotify.artist_list on spotify.artist_list.artist_id = tmp_artist.artist_id
                WHERE spotify.artist_list.artist_id IS NULL;

                DROP TABLE tmp_artist
                """
        )
        connection.commit()
        
        cur_eng.execute(
                """
                CREATE TEMP TABLE IF NOT EXISTS tmp_song_history AS SELECT * FROM spotify.song_history LIMIT 0
                """)

        history_song_frame.to_sql('song_history', con = engine, if_exists = 'append', index = False, schema = 'spotify')

        last_song_frame.to_sql('index', con = engine, if_exists = 'replace', index = False, schema = 'spotify')
        return "Finished loading song"

def main():
    spotify_etl_func()

if __name__=='__main__':
    main()