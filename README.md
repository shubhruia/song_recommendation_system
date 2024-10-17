# Spotify Recommendation System

A Streamlit web application that provides music recommendations based on a user's input of a song or playlist URL. This app uses the Spotify API to fetch song data, analyze it, and suggest similar songs and artists.

## Features

- **Song Analysis**: Input a Spotify song URL to get detailed information and recommendations.
- **Playlist Analysis**: Input a Spotify playlist URL to analyze its tracks and get recommendations based on a selected song.
- **Song Recommendations**: Get up to 8 song recommendations based on the input song or selected playlist track.
- **Artist Recommendations**: Discover up to 8 similar artists based on the input song or selected playlist track.
- **Genre Analysis**: View the genre distribution of playlist tracks in a pie chart.
- **Visual Presentation**: Display song and artist information with album covers and Spotify links.

## Demo

**Try the live demo of this application [here](https://songrecommendationsystem.streamlit.app/).**

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shubhruia/spotify-recommendation-system.git
   ```

2. **Install the required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Spotify API credentials**:
   - Create a Spotify Developer account and register your application to get a CLIENT_ID and CLIENT_SECRET.
   - Add these credentials to your Streamlit secrets or as environment variables.

## Usage

1. **Run the App**: Launch the app by running the following command in your terminal:
   ```bash
   streamlit run main.py
   ```

2. **Song Analysis**:
   - Select "Song" from the radio button options.
   - Enter a Spotify song URL in the text input field.
   - View the song details, recommended songs, and similar artists.

3. **Playlist Analysis**:
   - Select "Playlist" from the radio button options.
   - Enter a Spotify playlist URL in the text input field.
   - View the playlist tracks, genre distribution, and select a track for recommendations.

4. **Explore Recommendations**:
   - For both song and playlist inputs, explore the recommended songs and artists.
   - Click on the provided Spotify links to listen to the recommendations.

## Dependencies

- **[streamlit](https://streamlit.io/)**: For building the web app interface.
- **[spotipy](https://spotipy.readthedocs.io/)**: Python library for the Spotify Web API.
- **[pandas](https://pandas.pydata.org/)**: For data manipulation and analysis.
- **[plotly](https://plotly.com/python/)**: For creating interactive plots.
- **[requests](https://docs.python-requests.org/)**: For making HTTP requests.

## Contribution

Feel free to submit issues or pull requests if you find bugs or have suggestions for improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project uses the Spotify Web API for fetching music data.
- Thanks to the Streamlit team for providing an excellent framework for building data apps.
