import base64
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify Credentials
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

# Function to get Spotify access token
def get_access_token():
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data={'grant_type': 'client_credentials'}, headers=headers)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        st.error(f"Error obtaining access token: {response.status_code} - {response.text}")
        return None

# Function to get track data from a song URL
def get_song_data_from_url(song_url, access_token):
    sp = spotipy.Spotify(auth=access_token)
    try:
        track_id = song_url.split('/')[-1].split('?')[0]  # Extract track ID from URL
        track_info = sp.track(track_id)
        return track_info
    except Exception as e:
        st.error(f"Error fetching song data: {e}")
        return None

# Function to get playlist data from a playlist URL
def get_playlist_tracks_from_url(playlist_url, access_token):
    sp = spotipy.Spotify(auth=access_token)
    try:
        playlist_id = playlist_url.split('/')[-1].split('?')[0]  # Extract playlist ID from URL
        playlist_info = sp.playlist(playlist_id)  # Get full playlist info
        tracks = [track['track'] for track in playlist_info['tracks']['items'] if track['track'] is not None]  # Return valid tracks
        return playlist_info['name'], playlist_info['images'][0]['url'], tracks  # Return playlist name, image, and tracks
    except Exception as e:
        st.error(f"Error fetching playlist data: {e}")
        return None, None, []

# Function to get artist genres
def get_artist_genres(artist_id, sp):
    try:
        artist_info = sp.artist(artist_id)
        return artist_info.get('genres', [])[:3]  # Limit to 3 genres
    except Exception as e:
        st.error(f"Error fetching artist genres: {e}")
        return []

# Function to get similar songs
def get_similar_songs(track_id, sp):
    try:
        recommendations = sp.recommendations(seed_tracks=[track_id], limit=8)  # Change limit to 8
        return recommendations['tracks']
    except Exception as e:
        st.error(f"Error fetching similar songs: {e}")
        return []

# Streamlit app
st.title("Spotify Recommendation System")

input_type = st.radio("Select Input Type", ("Song", "Playlist"))

if input_type == "Song":
    song_url = st.text_input("Enter Song URL", "")
    if song_url:
        with st.spinner('Fetching song data...'):
            access_token = get_access_token()
            if access_token:
                # Initialize Spotify API client
                sp = spotipy.Spotify(auth=access_token)
                st.write("---")
                # Fetch song data from the provided URL
                track_info = get_song_data_from_url(song_url, access_token)
                if track_info:
                    track_id = track_info['id']
                    track_name = track_info['name']
                    track_artists = ', '.join([artist['name'] for artist in track_info['artists']])
                    track_genres = ', '.join(get_artist_genres(track_info['artists'][0]['id'], sp))

                    st.subheader("**You searched for:**")
                    st.image(track_info['album']['images'][0]['url'], width=150)
                    st.write(f"**Track Name**: {track_name}")
                    st.write(f"**Artists**: {track_artists}")
                    st.write(f"**Genres**: {track_genres}")
                    st.write(f"**Release Year**: {track_info['album']['release_date'][:4]}")
                    st.write("---")

                    # Get similar songs
                    similar_songs = get_similar_songs(track_id, sp)
                    if similar_songs:
                        st.subheader("**Recommended Songs**:")
                        cols = st.columns(4)  # Change to 4 columns
                        for i, song in enumerate(similar_songs):
                            with cols[i % 4]:  # Arrange songs per row
                                st.image(song['album']['images'][0]['url'], width=150)
                                st.write(f"**Track Name**: {song['name']}")
                                st.write(f"**Artists**: {', '.join([artist['name'] for artist in song['artists']])}")
                                song_genres = ', '.join(get_artist_genres(song['artists'][0]['id'], sp))  # Get genres for the song
                                st.write(f"**Genres**: {song_genres}")
                                st.write(f"**Release Year**: {song['album']['release_date'][:4]}")
                                st.write(f"[Listen here]({song['external_urls']['spotify']})")
                    st.write("---")

                    # Get similar artists
                    primary_artist_id = track_info['artists'][0]['id']
                    similar_artists = sp.artist_related_artists(primary_artist_id)['artists'][:8]  # Limit to 8 artists
                    if similar_artists:
                        st.subheader("**Artists you may like**:")
                        cols_artists = st.columns(4)  # Change to 4 columns
                        for i, artist in enumerate(similar_artists):
                            with cols_artists[i % 4]:  # Arrange artists per row
                                st.image(artist['images'][0]['url'], width=150)
                                st.write(f"**Artist Name**: {artist['name']}")
                                st.write(f"**Genres**: {', '.join(get_artist_genres(artist['id'], sp))}")  # Limit to 3 genres
                                st.write(f"**Popularity**: {artist['popularity']}")
                                st.write(f"[Listen here]({artist['external_urls']['spotify']})")
                    st.write("---")

elif input_type == "Playlist":
    playlist_url = st.text_input("Enter Playlist URL", "")
    if playlist_url:
        with st.spinner('Fetching playlist data...'):
            access_token = get_access_token()
            if access_token:
                # Initialize Spotify API client
                sp = spotipy.Spotify(auth=access_token)
                st.write("---")
                # Fetch playlist data from the provided URL
                playlist_name, playlist_image, playlist_tracks = get_playlist_tracks_from_url(playlist_url, access_token)
                if playlist_tracks:
                    # Show the playlist image and name
                    st.subheader("**You searched for:**")
                    st.image(playlist_image, width=150)
                    st.write(f"**Name**: {playlist_name}")
                    st.write("---")

                    # Create a dataframe to display playlist tracks
                    track_data = {
                        "Track Name": [track['name'] for track in playlist_tracks],
                        "Artists": [', '.join([artist['name'] for artist in track['artists']]) for track in playlist_tracks],
                        "Genres": [', '.join(get_artist_genres(track['artists'][0]['id'], sp)) for track in playlist_tracks],
                        "Release Year": [track['album']['release_date'][:4] for track in playlist_tracks]  # Extract release year
                    }
                    track_df = pd.DataFrame(track_data)

                    # Show the playlist tracks in a table
                    st.subheader("**Playlist Tracks**:")
                    st.dataframe(track_df)
                    st.write("---")

                    # Count the occurrences of each genre
                    genre_list = [genre for sublist in track_df['Genres'].str.split(', ') for genre in sublist if genre]
                    genre_counts = pd.Series(genre_list).value_counts()

                    # Display the genre distribution pie chart
                    st.subheader("**Looks like you like these genres**:")
                    fig = px.pie(genre_counts, values=genre_counts.values, names=genre_counts.index, title="Genre Distribution")
                    st.plotly_chart(fig)
                    st.write("---")

                    selected_track = st.selectbox("Select a track from the playlist", options=track_df.index, format_func=lambda x: track_df['Track Name'][x])

                    if selected_track is not None:
                        # Get selected track information
                        selected_track_info = playlist_tracks[selected_track]
                        selected_track_id = selected_track_info['id']
                        selected_track_name = selected_track_info['name']
                        selected_track_artists = ', '.join([artist['name'] for artist in selected_track_info['artists']])
                        selected_track_genres = ', '.join(get_artist_genres(selected_track_info['artists'][0]['id'], sp))

                        st.subheader("**You selected**:")
                        st.image(selected_track_info['album']['images'][0]['url'], width=150)
                        st.write(f"**Track Name**: {selected_track_name}")
                        st.write(f"**Artists**: {selected_track_artists}")
                        st.write(f"**Genres**: {selected_track_genres}")
                        st.write(f"**Release Year**: {selected_track_info['album']['release_date'][:4]}")
                        st.write("---")

                        # Get similar songs for the selected track
                        similar_songs = get_similar_songs(selected_track_id, sp)
                        if similar_songs:
                            st.subheader("**Recommended Songs**:")
                            cols = st.columns(4)  # Change to 4 columns
                            for i, song in enumerate(similar_songs):
                                with cols[i % 4]:  # Arrange songs per row
                                    st.image(song['album']['images'][0]['url'], width=150)
                                    st.write(f"**Track Name**: {song['name']}")
                                    st.write(f"**Artists**: {', '.join([artist['name'] for artist in song['artists']])}")
                                    song_genres = ', '.join(get_artist_genres(song['artists'][0]['id'], sp))  # Get genres for the song
                                    st.write(f"**Genres**: {song_genres}")
                                    st.write(f"**Release Year**: {song['album']['release_date'][:4]}")
                                    st.write(f"[Listen here]({song['external_urls']['spotify']})")
                        st.write("---")

                        # Get similar artists for the selected track
                        primary_artist_id = selected_track_info['artists'][0]['id']
                        similar_artists = sp.artist_related_artists(primary_artist_id)['artists'][:8]  # Limit to 8 artists
                        if similar_artists:
                            st.subheader("**Artists you may like**:")
                            cols_artists = st.columns(4)  # Change to 4 columns
                            for i, artist in enumerate(similar_artists):
                                with cols_artists[i % 4]:  # Arrange artists per row
                                    st.image(artist['images'][0]['url'], width=150)
                                    st.write(f"**Artist Name**: {artist['name']}")
                                    st.write(f"**Genres**: {', '.join(get_artist_genres(artist['id'], sp))}")  # Limit to 3 genres
                                    st.write(f"**Popularity**: {artist['popularity']}")
                                    st.write(f"[Listen here]({artist['external_urls']['spotify']})")
                        st.write("---")
