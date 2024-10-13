import streamlit as st
import requests
import base64
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Spotify Credentials
CLIENT_ID = 'be065b53d379455887640cdd3b887ae6'
CLIENT_SECRET = 'ae1668b0fd204395a57fced0ed0a74b2'

# Function to get Spotify access token
def get_access_token():
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data={'grant_type': 'client_credentials'}, headers=headers)

    return response.json()['access_token'] if response.status_code == 200 else st.error(f"Error obtaining access token: {response.status_code}")

# Batch function to get audio features and artist genres
def get_audio_features_and_genres(sp, track_ids, artist_ids):
    audio_features = sp.audio_features(tracks=track_ids)
    artist_genres = {}
    for i in range(0, len(artist_ids), 50):
        artists_info = sp.artists(artist_ids[i:i+50])['artists']
        artist_genres.update({artist['id']: artist.get('genres', []) for artist in artists_info})
    return audio_features, artist_genres

# Function to get playlist data
def get_trending_playlist_data(playlist_id, access_token):
    sp = spotipy.Spotify(auth=access_token)
    playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id, name, artists, album(id, name, images)))')['items']
    
    track_ids, artist_ids = [track['track']['id'] for track in playlist_tracks], {artist['id'] for track in playlist_tracks for artist in track['track']['artists']}
    audio_features, artist_genres = get_audio_features_and_genres(sp, track_ids, list(artist_ids))
    
    def get_track_data(i, track_info):
        track = track_info['track']
        track_data = {
            'Track Name': track['name'],
            'Artists': ', '.join([artist['name'] for artist in track['artists']]),
            'Album Name': track['album']['name'],
            'Album Image URL': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'Release Date': sp.album(track['album']['id']).get('release_date') if track['album']['id'] else None,
            'Popularity': sp.track(track['id']).get('popularity') if track['id'] else None,
            'Genre': ', '.join(artist_genres.get(track['artists'][0]['id'], ['Unknown'])),
            **{key: audio_features[i][key] for key in ['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']}
        }
        return track_data
    
    return pd.DataFrame([get_track_data(i, track_info) for i, track_info in enumerate(playlist_tracks)])

# Function to precompute similarity matrix
def precompute_similarity_matrix(music_df):
    features = music_df[['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']].values
    return cosine_similarity(MinMaxScaler().fit_transform(features))

# Function for content-based recommendations
def content_based_recommendations(input_song_name, music_df, similarity_matrix, num_recommendations=5):
    if input_song_name not in music_df['Track Name'].values:
        st.error(f"'{input_song_name}' not found in the dataset.")
        return None
    
    input_song_index = music_df[music_df['Track Name'] == input_song_name].index[0]
    similar_songs = music_df.iloc[similarity_matrix[input_song_index].argsort()[::-1][1:num_recommendations+1]]

    return similar_songs[['Track Name', 'Artists', 'Album Name', 'Release Date', 'Popularity', 'Album Image URL', 'Genre']]

# Function to get similar artists for the input song's artist
def get_similar_artists(artist_id, sp):
    try:
        similar_artists = sp.artist_related_artists(artist_id)['artists']
        artist_data = []
        for artist in similar_artists[:5]:  # Limit to top 5 similar artists
            artist_info = {
                'Artist Name': artist['name'],
                'Genres': ', '.join(artist['genres']) if artist['genres'] else 'Unknown',
                'Popularity': artist['popularity'],
                'Followers': artist['followers']['total'],
                'Image URL': artist['images'][0]['url'] if artist['images'] else None
            }
            artist_data.append(artist_info)
        return artist_data
    except Exception as e:
        st.error(f"Error fetching similar artists: {e}")
        return []

# Streamlit app - add artist recommendations section
st.title("Spotify Playlist Song Recommender")

playlist_id = st.text_input("Enter Spotify Playlist ID", "")
if playlist_id:
    access_token = get_access_token()
    if access_token:
        # Initialize Spotify API client
        sp = spotipy.Spotify(auth=access_token)
        
        music_df = get_trending_playlist_data(playlist_id, access_token)
        similarity_matrix = precompute_similarity_matrix(music_df)

        st.write("Playlist Data")
        st.dataframe(music_df[['Track Name', 'Artists', 'Album Name', 'Popularity', 'Genre', 'Release Date']])

    input_song_name = st.text_input("Enter a song from the playlist for recommendations")
    if input_song_name:
        # Content-based song recommendations
        recommendations = content_based_recommendations(input_song_name, music_df, similarity_matrix)
        if recommendations is not None:
            st.write(f"Recommended music similar to '{input_song_name}':")
            for _, row in recommendations.iterrows():
                st.image(row['Album Image URL'], width=150)
                st.write(f"**Track Name**: {row['Track Name']}")
                st.write(f"**Artists**: {row['Artists']}")
                st.write(f"**Album Name**: {row['Album Name']}")
                st.write(f"**Genre**: {row['Genre']}")
                st.write(f"**Popularity**: {row['Popularity']}")
                st.write(f"**Release Date**: {row['Release Date']}")
                st.write("---")

            # Artist recommendation section
            st.write(f"Artists you might like based on '{input_song_name}'")

            # Get the primary artist of the input song
            input_song = music_df[music_df['Track Name'] == input_song_name].iloc[0]
            primary_artist_name = input_song['Artists'].split(",")[0]
            
            # Get artist ID from Spotify
            artist_results = sp.search(q=f'artist:{primary_artist_name}', type='artist')
            if artist_results['artists']['items']:
                primary_artist_id = artist_results['artists']['items'][0]['id']
                similar_artists = get_similar_artists(primary_artist_id, sp)
                
                if similar_artists:
                    for artist in similar_artists:
                        st.image(artist['Image URL'], width=150)
                        st.write(f"**Artist Name**: {artist['Artist Name']}")
                        st.write(f"**Genres**: {artist['Genres']}")
                        st.write(f"**Popularity**: {artist['Popularity']}")
                        st.write(f"**Followers**: {artist['Followers']}")
                        st.write("---")
            else:
                st.error(f"No artist found for '{primary_artist_name}'")