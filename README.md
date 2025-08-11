# Spotify lyric display

Searches up the lyrics for the song currently playing on spotify (from Genius.com) and shows it.
The top bar shows lists songs of the song's album to select and play directly.
The left sidebar features the song cover as well as controls to pause/skip the song, adjust audio and
change the output device (other connected spotify clients e.g. when the app is opened on the phone and PC).
<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/4263ca50-6677-44d4-8525-843968e3044d" />

# Installation on Windows (Requires Python 3)
# Step 1: Create .env files to store the required api keys
Create a file .env with the following exports in the root directory and fill the blank values.

    <root directory>/.env

    export GENIUS_ACCESS_TOKEN="<GENIUS API KEY HERE>"
    export SPOTIPY_ACCOUNT_NAME="<SPOTIFY USERNAME>"
    export SPOTIPY_CLIENT_ID="<Spotify Developer CLIENT ID>"
    export SPOTIPY_CLIENT_SECRET="<Spotify Developer CLIENT SECRET>"
    export SPOTIPY_REDIRECT_URI="<Spotify Developer REDIRECT URI>"

You need to create an app on [spotify's developer page](https://developer.spotify.com/dashboard/applications) to get the client-id, client-secret and redirect uri.
The Redirect URI can be a local adress i.e.:

    http://localhost:5000/auth/

To get the Genius Access Token you also need to create an app on the [Genius developer page](https://genius.com/api-clients/new).
After that you can click the 'Generate Access Token' button and imply paste the token into the .env file.

# Step 2: Create the virtual environment and install the required modules
#### 1. Create the virtual environment
To do this you need to install [venv](https://docs.python.org/3/library/venv.html) if you haven't already.
This allows you to store the modules needed for this project inside it's own local folder.

The first step is to open the windows console and create the virtual environment.

    python -m venv .\venv

This will create a new folder named 'venv' where we will store all required modules.


The next step is to activate the environment. To do this, simply call the activate file inside the virtual environment folder:

    .\venv\Scripts\activate

You should now see '(venv)' at the beginning of your console, this means you're now using the virtual environment and python uses the virtual environment for further actions.

#### 2. Install the required modules 
The requirements.txt contains all required modules.
To install them simply use pip:

    python -m pip install -r requirements.txt

This should install all required modules and store them inside the virtual environment inside ./venv/Lib/

#### 3. Start the main.py

    python main.py

#### 4. Pass in the redirect uri
When you first start the programm, the spotify api requires you to authenticate with your accoumt. In order to do this, a http request is send to Spotify asking for authentication. Spotify responds with a URL that gets opened in your web browser automatically.
You might need to pass this URL into the program by simply copy&pasting it into the console.

#### Note: Make sure you created the .env file correctly (see Step 1)

You will see something like this pop up inside the console:

    User authentication requires interaction with your
    web browser. Once you enter your credentials and
    give authorization, you will be redirected to
    a url.  Paste that url you were directed to to
    complete the authorization.


    Opened https://accounts.spotify.com/authorize?client_id=<CLIENTID>&response_type=code&redirect_uri=<Your redirect uri with a code> in your browser

To continue just copy the url from the browser's address bar and paste it in into the console. After hitting enter you should be good to go.

If you experience problems, make sure spotify is playing a song and you're not listening in private mode.

# Used Libraries
This project mainly uses the LyricsGenius library by johnwmillr [Github](https://github.com/johnwmillr/LyricsGenius) and the spotipy library by plamere [Github](https://github.com/plamere/spotipy).
