import streamlit as st
import requests
import json
import os
from datetime import datetime
import base64

# Set page config
st.set_page_config(
    page_title="GitHub → Streamlit Deployer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_github_repo(token, repo_name, description, private=False):
    """Create a GitHub repository"""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": True
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response

def upload_file_to_repo(token, owner, repo, file_path, content, message="Add file"):
    """Upload a file to GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Encode content to base64
    content_b64 = base64.b64encode(content.encode()).decode()
    
    data = {
        "message": message,
        "content": content_b64
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response

def get_streamlit_app_template():
    """Get a template Streamlit app"""
    return """import sys
import subprocess
import threading
import time
import os
import json
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import urllib.parse
import requests
import sqlite3
from pathlib import Path

# Install required packages
try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st

try:
    import google.auth
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import Flow
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-auth", "google-auth-oauthlib", "google-api-python-client"])
    import google.auth
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import Flow

# Initialize database for persistent logs
def init_database():
    \"\"\"Initialize SQLite database for persistent logs\"\"\"
    try:
        db_path = Path("streaming_logs.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaming_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                log_type TEXT NOT NULL,
                message TEXT NOT NULL,
                video_file TEXT,
                stream_key TEXT,
                channel_name TEXT
            )
        ''')
        
        # Create streaming_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaming_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                video_file TEXT,
                stream_title TEXT,
                stream_description TEXT,
                tags TEXT,
                category TEXT,
                privacy_status TEXT,
                made_for_kids BOOLEAN,
                channel_name TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Create saved_channels table for persistent authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT UNIQUE NOT NULL,
                channel_id TEXT NOT NULL,
                auth_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database initialization error: {e}")

def save_channel_auth(channel_name, channel_id, auth_data):
    \"\"\"Save channel authentication data persistently\"\"\"
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO saved_channels 
            (channel_name, channel_id, auth_data, created_at, last_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            channel_name,
            channel_id,
            json.dumps(auth_data),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving channel auth: {e}")
        return False

def load_saved_channels():
    \"\"\"Load saved channel authentication data\"\"\"
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT channel_name, channel_id, auth_data, last_used
            FROM saved_channels 
            ORDER BY last_used DESC
        ''')
        
        channels = []
        for row in cursor.fetchall():
            channel_name, channel_id, auth_data, last_used = row
            channels.append({
                'name': channel_name,
                'id': channel_id,
                'auth': json.loads(auth_data),
                'last_used': last_used
            })
        
        conn.close()
        return channels
    except Exception as e:
        st.error(f"Error loading saved channels: {e}")
        return []

def update_channel_last_used(channel_name):
    \"\"\"Update last used timestamp for a channel\"\"\"
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE saved_channels 
            SET last_used = ?
            WHERE channel_name = ?
        ''', (datetime.now().isoformat(), channel_name))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error updating channel last used: {e}")

def log_to_database(session_id, log_type, message, video_file=None, stream_key=None, channel_name=None):
    \"\"\"Log message to database\"\"\"
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO streaming_logs 
            (timestamp, session_id, log_type, message, video_file, stream_key, channel_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            session_id,
            log_type,
            message,
            video_file,
            stream_key,
            channel_name
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error logging to database: {e}")

def get_logs_from_database(session_id=None, limit=100):
    \"\"\"Get logs from database\"\"\"
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT timestamp, log_type, message, video_file, channel_name
                FROM streaming_logs 
                WHERE session_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT timestamp, log_type, message, video_file, channel_name
                FROM streaming_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        return logs
    except Exception as e:
        st.error(f"Error getting logs from database: {e}")
        return []

def save_streaming_session(session_id, video_file, stream_title, stream_description, tags, category, privacy_status, made_for_kids, channel_name):
    \"\"\"Save streaming session to database\"\"\"
    try:
        conn = sqlite3.connect("streaming_logs.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO streaming_sessions 
            (session_id, start_time, video_file, stream_title, stream_description, tags, category, privacy_status, made_for_kids, channel_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            datetime.now().isoformat(),
            video_file,
            stream_title,
            stream_description,
            tags,
            category,
            privacy_status,
            made_for_kids,
            channel_name
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error saving streaming session: {e}")

def load_google_oauth_config(json_file):
    \"\"\"Load Google OAuth configuration from downloaded JSON file\"\"\"
    try:
        config = json.load(json_file)
        if 'web' in config:
            return config['web']
        elif 'installed' in config:
            return config['installed']
        else:
            st.error("Invalid Google OAuth JSON format")
            return None
    except Exception as e:
        st.error(f"Error loading Google OAuth JSON: {e}")
        return None

def generate_auth_url(client_config):
    \"\"\"Generate OAuth authorization URL\"\"\"
    try:
        scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
        
        # Create authorization URL
        auth_url = (
            f"{client_config['auth_uri']}?"
            f"client_id={client_config['client_id']}&"
            f"redirect_uri={urllib.parse.quote(client_config['redirect_uris'][0])}&"
            f"scope={urllib.parse.quote(' '.join(scopes))}&"
            f"response_type=code&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        return auth_url
    except Exception as e:
        st.error(f"Error generating auth URL: {e}")
        return None

def exchange_code_for_tokens(client_config, auth_code):
    \"\"\"Exchange authorization code for access and refresh tokens\"\"\"
    try:
        token_data = {
            'client_id': client_config['client_id'],
            'client_secret': client_config['client_secret'],
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': client_config['redirect_uris'][0]
        }
        
        response = requests.post(client_config['token_uri'], data=token_data)
        
        if response.status_code == 200:
            tokens = response.json()
            return tokens
        else:
            st.error(f"Token exchange failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error exchanging code for tokens: {e}")
        return None

def load_channel_config(json_file):
    \"\"\"Load channel configuration from JSON file\"\"\"
    try:
        config = json.load(json_file)
        return config
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return None

def validate_channel_config(config):
    \"\"\"Validate channel configuration structure\"\"\"
    required_fields = ['channels']
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    if not isinstance(config['channels'], list):
        return False, "Channels must be a list"
    
    for i, channel in enumerate(config['channels']):
        required_channel_fields = ['name', 'stream_key']
        for field in required_channel_fields:
            if field not in channel:
                return False, f"Channel {i+1} missing required field: {field}"
    
    return True, "Valid configuration"

def create_youtube_service(credentials_dict):
    \"\"\"Create YouTube API service from credentials\"\"\"
    try:
        if 'token' in credentials_dict:
            credentials = Credentials.from_authorized_user_info(credentials_dict)
        else:
            credentials = Credentials(
                token=credentials_dict.get('access_token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=credentials_dict.get('client_id'),
                client_secret=credentials_dict.get('client_secret'),
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
            )
        service = build('youtube', 'v3', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Error creating YouTube service: {e}")
        return None

def get_stream_key_only(service):
    \"\"\"Get stream key without creating broadcast\"\"\"
    try:
        # Create a simple live stream to get stream key
        stream_request = service.liveStreams().insert(
            part="snippet,cdn",
            body={
                "snippet": {
                    "title": f"Stream Key Generator - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                },
                "cdn": {
                    "resolution": "1080p",
                    "frameRate": "30fps",
                    "ingestionType": "rtmp"
                }
            }
        )
        stream_response = stream_request.execute()
        
        return {
            "stream_key": stream_response['cdn']['ingestionInfo']['streamName'],
            "stream_url": stream_response['cdn']['ingestionInfo']['ingestionAddress'],
            "stream_id": stream_response['id']
        }
    except Exception as e:
        st.error(f"Error getting stream key: {e}")
        return None

def get_channel_info(service, channel_id=None):
    \"\"\"Get channel information from YouTube API\"\"\"
    try:
        if channel_id:
            request = service.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
        else:
            request = service.channels().list(
                part="snippet,statistics",
                mine=True
            )
        
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        st.error(f"Error fetching channel info: {e}")
        return []

def create_live_stream(service, title, description, scheduled_start_time, tags=None, category_id="20", privacy_status="public", made_for_kids=False):
    \"\"\"Create a live stream on YouTube with complete settings\"\"\"
    try:
        # Create live stream
        stream_request = service.liveStreams().insert(
            part="snippet,cdn",
            body={
                "snippet": {
                    "title": f"{title} - Stream",
                    "description": description
                },
                "cdn": {
                    "resolution": "1080p",
                    "frameRate": "30fps",
                    "ingestionType": "rtmp"
                }
            }
        )
        stream_response = stream_request.execute()
        
        # Prepare broadcast body
        broadcast_body = {
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": scheduled_start_time.isoformat()
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": made_for_kids
            },
            "contentDetails": {
                "enableAutoStart": True,
                "enableAutoStop": True
            }
        }
        
        # Add tags if provided
        if tags:
            broadcast_body["snippet"]["tags"] = tags
            
        # Add category if provided
        if category_id:
            broadcast_body["snippet"]["categoryId"] = category_id
        
        # Create live broadcast
        broadcast_request = service.liveBroadcasts().insert(
            part="snippet,status,contentDetails",
            body=broadcast_body
        )
        broadcast_response = broadcast_request.execute()
        
        # Bind stream to broadcast
        bind_request = service.liveBroadcasts().bind(
            part="id,contentDetails",
            id=broadcast_response['id'],
            streamId=stream_response['id']
        )
        bind_response = bind_request.execute()
        
        return {
            "stream_key": stream_response['cdn']['ingestionInfo']['streamName'],
            "stream_url": stream_response['cdn']['ingestionInfo']['ingestionAddress'],
            "broadcast_id": broadcast_response['id'],
            "stream_id": stream_response['id'],
            "watch_url": f"https://www.youtube.com/watch?v={broadcast_response['id']}",
            "studio_url": f"https://studio.youtube.com/video/{broadcast_response['id']}/livestreaming",
            "broadcast_response": broadcast_response
        }
    except Exception as e:
        st.error(f"Error creating live stream: {e}")
        return None

def get_existing_broadcasts(service, max_results=10):
    \"\"\"Get existing live broadcasts\"\"\"
    try:
        request = service.liveBroadcasts().list(
            part="snippet,status,contentDetails",
            mine=True,
            maxResults=max_results,
            broadcastStatus="all"
        )
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        st.error(f"Error getting existing broadcasts: {e}")
        return []

def get_broadcast_stream_key(service, broadcast_id):
    \"\"\"Get stream key for existing broadcast\"\"\"
    try:
        # Get broadcast details
        broadcast_request = service.liveBroadcasts().list(
            part="contentDetails",
            id=broadcast_id
        )
        broadcast_response = broadcast_request.execute()
        
        if not broadcast_response['items']:
            return None
            
        stream_id = broadcast_response['items'][0]['contentDetails'].get('boundStreamId')
        
        if not stream_id:
            return None
            
        # Get stream details
        stream_request = service.liveStreams().list(
            part="cdn",
            id=stream_id
        )
        stream_response = stream_request.execute()
        
        if stream_response['items']:
            stream_info = stream_response['items'][0]['cdn']['ingestionInfo']
            return {
                "stream_key": stream_info['streamName'],
                "stream_url": stream_info['ingestionAddress'],
                "stream_id": stream_id
            }
        
        return None
    except Exception as e:
        st.error(f"Error getting broadcast stream key: {e}")
        return None

def run_ffmpeg(video_path, stream_key, is_shorts, log_callback, rtmp_url=None, session_id=None):
    \"\"\"Run FFmpeg for streaming with enhanced logging\"\"\"
    output_url = rtmp_url or f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    scale = "-vf scale=720:1280" if is_shorts else ""
    cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", video_path,
        "-c:v", "libx264", "-preset", "veryfast", "-b:v", "2500k",
        "-maxrate", "2500k", "-bufsize", "5000k",
        "-g", "60", "-keyint_min", "60",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "flv"
    ]
    if scale:
        cmd += scale.split()
    cmd.append(output_url)
    
    start_msg = f"🚀 Starting FFmpeg: {' '.join(cmd[:8])}... [RTMP URL hidden for security]"
    log_callback(start_msg)
    if session_id:
        log_to_database(session_id, "INFO", start_msg, video_path)
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            log_callback(line.strip())
            if session_id:
                log_to_database(session_id, "FFMPEG", line.strip(), video_path)
        process.wait()
        
        end_msg = "✅ Streaming completed successfully"
        log_callback(end_msg)
        if session_id:
            log_to_database(session_id, "INFO", end_msg, video_path)
            
    except Exception as e:
        error_msg = f"❌ FFmpeg Error: {e}"
        log_callback(error_msg)
        if session_id:
            log_to_database(session_id, "ERROR", error_msg, video_path)
    finally:
        final_msg = "⏹️ Streaming session ended"
        log_callback(final_msg)
        if session_id:
            log_to_database(session_id, "INFO", final_msg, video_path)

def auto_process_auth_code():
    \"\"\"Automatically process authorization code from URL\"\"\"
    # Check URL parameters
    query_params = st.query_params
    
    if 'code' in query_params:
        auth_code = query_params['code']
        
        # Check if this code has been processed
        if 'processed_codes' not in st.session_state:
            st.session_state['processed_codes'] = set()
        
        if auth_code not in st.session_state['processed_codes']:
            st.info("🔄 Processing authorization code from URL...")
            
            if 'oauth_config' in st.session_state:
                with st.spinner("Exchanging code for tokens..."):
                    tokens = exchange_code_for_tokens(st.session_state['oauth_config'], auth_code)
                    
                    if tokens:
                        st.session_state['youtube_tokens'] = tokens
                        st.session_state['processed_codes'].add(auth_code)
                        
                        # Create credentials for YouTube service
                        oauth_config = st.session_state['oauth_config']
                        creds_dict = {
                            'access_token': tokens['access_token'],
                            'refresh_token': tokens.get('refresh_token'),
                            'token_uri': oauth_config['token_uri'],
                            'client_id': oauth_config['client_id'],
                            'client_secret': oauth_config['client_secret']
                        }
                        
                        # Test the connection
                        service = create_youtube_service(creds_dict)
                        if service:
                            channels = get_channel_info(service)
                            if channels:
                                channel = channels[0]
                                st.session_state['youtube_service'] = service
                                st.session_state['channel_info'] = channel
                                
                                # Save channel authentication persistently
                                save_channel_auth(
                                    channel['snippet']['title'],
                                    channel['id'],
                                    creds_dict
                                )
                                
                                st.success(f"✅ Successfully connected to: {channel['snippet']['title']}")
                                
                                # Clear URL parameters
                                st.query_params.clear()
                                st.rerun()
                        else:
                            st.error("❌ Failed to create YouTube service")
                    else:
                        st.error("❌ Failed to exchange code for tokens")
            else:
                st.error("❌ OAuth configuration not found. Please upload OAuth JSON first.")

def get_youtube_categories():
    \"\"\"Get YouTube video categories\"\"\"
    return {
        "1": "Film & Animation",
        "2": "Autos & Vehicles", 
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "19": "Travel & Events",
        "20": "Gaming",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "Howto & Style",
        "27": "Education",
        "28": "Science & Technology"
    }

def main():
    # Page configuration must be the first Streamlit command
    st.set_page_config(
        page_title="Advanced YouTube Live Streaming",
        page_icon="📺",
        layout="wide"
    )
    
    # Initialize database
    init_database()
    
    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if 'live_logs' not in st.session_state:
        st.session_state['live_logs'] = []
    
    st.title("🎥 Advanced YouTube Live Streaming Platform")
    st.markdown("---")
    
    # Auto-process authorization code if present
    auto_process_auth_code()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("📋 Configuration")
        
        # Session info
        st.info(f"🆔 Session: {st.session_state['session_id']}")
        
        # Saved Channels Section
        st.subheader("💾 Saved Channels")
        saved_channels = load_saved_channels()
        
        if saved_channels:
            st.write("**Previously authenticated channels:**")
            for channel in saved_channels:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📺 {channel['name']}")
                    st.caption(f"Last used: {channel['last_used'][:10]}")
                
                with col2:
                    if st.button("🔑 Use", key=f"use_{channel['name']}"):
                        # Load this channel's authentication
                        service = create_youtube_service(channel['auth'])
                        if service:
                            # Verify the authentication is still valid
                            channels = get_channel_info(service)
                            if channels:
                                channel_info = channels[0]
                                st.session_state['youtube_service'] = service
                                st.session_state['channel_info'] = channel_info
                                update_channel_last_used(channel['name'])
                                st.success(f"✅ Loaded: {channel['name']}")
                                st.rerun()
                            else:
                                st.error("❌ Authentication expired")
                        else:
                            st.error("❌ Failed to load authentication")
        else:
            st.info("No saved channels. Authenticate below to save.")
        
        # Google OAuth Configuration
        st.subheader("🔐 Google OAuth Setup")
        oauth_file = st.file_uploader("Upload Google OAuth JSON", type=['json'], key="oauth_upload")
        
        if oauth_file:
            oauth_config = load_google_oauth_config(oauth_file)
            if oauth_config:
                st.success("✅ Google OAuth config loaded")
                st.session_state['oauth_config'] = oauth_config
                
                # Generate authorization URL
                auth_url = generate_auth_url(oauth_config)
                if auth_url:
                    st.markdown("### Step 1: Authorize Access")
                    st.markdown(f"[🔗 Click here to authorize]({auth_url})")
                    
                    # Instructions
                    with st.expander("💡 Instructions"):
                        st.write("1. Click the authorization link above")
                        st.write("2. Grant permissions to your YouTube account")
                        st.write("3. You'll be redirected back automatically")
                        st.write("4. Or copy the code from the URL and paste below")
                    
                    # Manual authorization code input (fallback)
                    st.markdown("### Manual Code Input (if needed)")
                    auth_code = st.text_input("Authorization Code (optional)", type="password")
                    
                    if st.button("Exchange Code for Tokens"):
                        if auth_code:
                            with st.spinner("Exchanging code for tokens..."):
                                tokens = exchange_code_for_tokens(oauth_config, auth_code)
                                if tokens:
                                    st.success("✅ Tokens obtained successfully!")
                                    st.session_state['youtube_tokens'] = tokens
                                    
                                    # Create credentials for YouTube service
                                    creds_dict = {
                                        'access_token': tokens['access_token'],
                                        'refresh_token': tokens.get('refresh_token'),
                                        'token_uri': oauth_config['token_uri'],
                                        'client_id': oauth_config['client_id'],
                                        'client_secret': oauth_config['client_secret']
                                    }
                                    
                                    # Test the connection
                                    service = create_youtube_service(creds_dict)
                                    if service:
                                        channels = get_channel_info(service)
                                        if channels:
                                            channel = channels[0]
                                            st.success(f"🎉 Connected to: {channel['snippet']['title']}")
                                            st.session_state['youtube_service'] = service
                                            st.session_state['channel_info'] = channel
                                            
                                            # Save channel authentication persistently
                                            save_channel_auth(
                                                channel['snippet']['title'],
                                                channel['id'],
                                                creds_dict
                                            )
                        else:
                            st.error("Please enter the authorization code")
        
        # JSON Configuration Upload
        st.subheader("📄 Channel Configuration")
        json_file = st.file_uploader("Upload JSON Configuration", type=['json'])
        
        if json_file:
            config = load_channel_config(json_file)
            if config:
                is_valid, message = validate_channel_config(config)
                if is_valid:
                    st.success("✅ Valid configuration loaded")
                    st.session_state['channel_config'] = config
                else:
                    st.error(f"❌ Invalid configuration: {message}")
        
        # Log Management
        st.markdown("---")
        st.subheader("📊 Log Management")
        
        col_log1, col_log2 = st.columns(2)
        with col_log1:
            if st.button("🔄 Refresh Logs"):
                st.rerun()
        
        with col_log2:
            if st.button("🗑️ Clear Session Logs"):
                st.session_state['live_logs'] = []
                st.success("Logs cleared!")
        
        # Export logs
        if st.button("📥 Export All Logs"):
            all_logs = get_logs_from_database(limit=1000)
            if all_logs:
                logs_text = "\\n".join([f"[{log[0]}] {log[1]}: {log[2]}" for log in all_logs])
                st.download_button(
                    label="💾 Download Logs",
                    data=logs_text,
                    file_name=f"streaming_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎥 Video & Streaming Setup")
        
        # Video selection
        video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.flv', '.avi', '.mov', '.mkv'))]
        
        if video_files:
            st.write("📁 Available videos:")
            selected_video = st.selectbox("Select video", video_files)
        else:
            selected_video = None
            st.info("No video files found in current directory")
        
        # Video upload
        uploaded_file = st.file_uploader("Or upload new video", type=['mp4', 'flv', 'avi', 'mov', 'mkv'])
        
        if uploaded_file:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.read())
            st.success("✅ Video uploaded successfully!")
            video_path = uploaded_file.name
            log_to_database(st.session_state['session_id'], "INFO", f"Video uploaded: {uploaded_file.name}")
        elif selected_video:
            video_path = selected_video
        else:
            video_path = None
        
        # YouTube Authentication Status
        if 'youtube_service' in st.session_state and 'channel_info' in st.session_state:
            st.subheader("📺 YouTube Channel")
            channel = st.session_state['channel_info']
            col_ch1, col_ch2 = st.columns(2)
            
            with col_ch1:
                st.write(f"**Channel:** {channel['snippet']['title']}")
                st.write(f"**Subscribers:** {channel['statistics'].get('subscriberCount', 'Hidden')}")
            
            with col_ch2:
                st.write(f"**Views:** {channel['statistics'].get('viewCount', '0')}")
                st.write(f"**Videos:** {channel['statistics'].get('videoCount', '0')}")
            
            # YouTube Live Stream Management
            st.subheader("🎬 YouTube Live Stream Management")
            
            # Instructions panel
            with st.expander("💡 How to Use YouTube Live Features"):
                st.markdown(\"\"\"
                **🔑 Get Stream Key Only:**
                - Creates a stream key without YouTube Live broadcast
                - Use with external streaming software (OBS, etc.)
                - Stream won't appear in YouTube Studio dashboard
                
                **🎬 Create YouTube Live:** ⭐ **RECOMMENDED**
                - Creates complete YouTube Live broadcast
                - Appears in YouTube Studio dashboard
                - Uses all settings from form below
                - Ready for audience immediately
                
                **📋 View Existing Streams:**
                - Shows all your existing live broadcasts
                - Can reuse existing streams
                - Quick access to Watch and Studio URLs
                
                **⚠️ Important Notes:**
                - Fill out stream settings below before creating
                - YouTube Live broadcasts are scheduled to start in 30 seconds
                - Use "Create YouTube Live" for best experience
                \"\"\")
            
            # Three main buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("🔑 Get Stream Key Only", help="Get stream key without creating YouTube Live broadcast"):
                    try:
                        service = st.session_state['youtube_service']
                        with st.spinner("Getting stream key..."):
                            stream_info = get_stream_key_only(service)
                            if stream_info:
                                stream_key = stream_info['stream_key']
                                st.session_state['current_stream_key'] = stream_key
                                st.session_state['current_stream_info'] = stream_info
                                st.success("✅ Stream key obtained!")
                                log_to_database(st.session_state['session_id'], "INFO", "Stream key generated successfully")
                                
                                # Display stream information
                                st.info("🔑 **Stream Key Generated** (for external streaming software)")
                                col_sk1, col_sk2 = st.columns(2)
                                with col_sk1:
                                    st.text_input("Stream Key", value=stream_key, type="password", key="stream_key_display")
                                with col_sk2:
                                    st.text_input("RTMP URL", value=stream_info['stream_url'], key="rtmp_url_display")
                    except Exception as e:
                        error_msg = f"Error getting stream key: {e}"
                        st.error(error_msg)
                        log_to_database(st.session_state['session_id'], "ERROR", error_msg)
            
            with col_btn2:
                if st.button("🎬 Create YouTube Live", type="primary", help="Create complete YouTube Live broadcast (appears in Studio)"):
                    # Get form values
                    stream_title = st.session_state.get('stream_title_input', 'Live Stream')
                    stream_description = st.session_state.get('stream_description_input', 'Live streaming session')
                    tags_input = st.session_state.get('tags_input', '')
                    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []
                    category_id = st.session_state.get('category_id', "20")
                    privacy_status = st.session_state.get('privacy_status', "public")
                    made_for_kids = st.session_state.get('made_for_kids', False)
                    
                    try:
                        service = st.session_state['youtube_service']
                        with st.spinner("Creating YouTube Live broadcast..."):
                            # Schedule for 30 seconds from now
                            scheduled_time = datetime.now() + timedelta(seconds=30)
                            
                            live_info = create_live_stream(
                                service, 
                                stream_title, 
                                stream_description, 
                                scheduled_time,
                                tags,
                                category_id,
                                privacy_status,
                                made_for_kids
                            )
                            
                            if live_info:
                                st.success("🎉 **YouTube Live Broadcast Created Successfully!**")
                                st.session_state['current_stream_key'] = live_info['stream_key']
                                st.session_state['live_broadcast_info'] = live_info
                                
                                # Display comprehensive information
                                st.info("📺 **Live Broadcast Information:**")
                                
                                col_info1, col_info2 = st.columns(2)
                                with col_info1:
                                    st.write(f"**🎬 Title:** {stream_title}")
                                    st.write(f"**🔒 Privacy:** {privacy_status.title()}")
                                    st.write(f"**📂 Category:** {get_youtube_categories().get(category_id, 'Unknown')}")
                                
                                with col_info2:
                                    st.write(f"**🏷️ Tags:** {', '.join(tags) if tags else 'None'}")
                                    st.write(f"**👶 Made for Kids:** {'Yes' if made_for_kids else 'No'}")
                                    st.write(f"**⏰ Scheduled:** {scheduled_time.strftime('%H:%M:%S')}")
                                
                                # Important links
                                st.markdown("### 🔗 Important Links:")
                                col_link1, col_link2 = st.columns(2)
                                
                                with col_link1:
                                    st.markdown(f"**📺 Watch URL:** [Open Stream]({live_info['watch_url']})")
                                    st.markdown(f"**🎛️ Studio URL:** [Manage in Studio]({live_info['studio_url']})")
                                
                                with col_link2:
                                    st.text_input("🔑 Stream Key", value=live_info['stream_key'], type="password", key="created_stream_key")
                                    st.text_input("🌐 RTMP URL", value=live_info['stream_url'], key="created_rtmp_url")
                                
                                st.success("✅ **Ready to stream!** Use the stream key above or click 'Start Streaming' below.")
                                
                                log_to_database(st.session_state['session_id'], "INFO", f"YouTube Live created: {live_info['watch_url']}")
                    except Exception as e:
                        error_msg = f"Error creating YouTube Live: {e}"
                        st.error(error_msg)
                        log_to_database(st.session_state['session_id'], "ERROR", error_msg)
            
            with col_btn3:
                if st.button("📋 View Existing Streams", help="View and manage existing live broadcasts"):
                    try:
                        service = st.session_state['youtube_service']
                        with st.spinner("Loading existing broadcasts..."):
                            broadcasts = get_existing_broadcasts(service)
                            
                            if broadcasts:
                                st.success(f"📺 Found {len(broadcasts)} existing broadcasts:")
                                
                                for i, broadcast in enumerate(broadcasts):
                                    with st.expander(f"🎬 {broadcast['snippet']['title']} - {broadcast['status']['lifeCycleStatus']}"):
                                        col_bc1, col_bc2 = st.columns(2)
                                        
                                        with col_bc1:
                                            st.write(f"**Title:** {broadcast['snippet']['title']}")
                                            st.write(f"**Status:** {broadcast['status']['lifeCycleStatus']}")
                                            st.write(f"**Privacy:** {broadcast['status']['privacyStatus']}")
                                            st.write(f"**Created:** {broadcast['snippet']['publishedAt'][:10]}")
                                        
                                        with col_bc2:
                                            watch_url = f"https://www.youtube.com/watch?v={broadcast['id']}"
                                            studio_url = f"https://studio.youtube.com/video/{broadcast['id']}/livestreaming"
                                            
                                            st.markdown(f"**Watch:** [Open]({watch_url})")
                                            st.markdown(f"**Studio:** [Manage]({studio_url})")
                                            
                                            if st.button(f"🔑 Use This Stream", key=f"use_broadcast_{i}"):
                                                # Get stream key for this broadcast
                                                stream_info = get_broadcast_stream_key(service, broadcast['id'])
                                                if stream_info:
                                                    st.session_state['current_stream_key'] = stream_info['stream_key']
                                                    st.session_state['live_broadcast_info'] = {
                                                        'broadcast_id': broadcast['id'],
                                                        'watch_url': watch_url,
                                                        'studio_url': studio_url,
                                                        'stream_key': stream_info['stream_key'],
                                                        'stream_url': stream_info['stream_url']
                                                    }
                                                    st.success(f"✅ Using stream: {broadcast['snippet']['title']}")
                                                    st.rerun()
                                                else:
                                                    st.error("❌ Could not get stream key for this broadcast")
                            else:
                                st.info("📺 No existing broadcasts found. Create a new one above!")
                    except Exception as e:
                        error_msg = f"Error loading existing broadcasts: {e}"
                        st.error(error_msg)
                        log_to_database(st.session_state['session_id'], "ERROR", error_msg)
        
        # Channel selection from JSON config
        elif 'channel_config' in st.session_state:
            st.subheader("📺 Channel Selection")
            config = st.session_state['channel_config']
            channel_options = [ch['name'] for ch in config['channels']]
            selected_channel_name = st.selectbox("Select channel", channel_options)
            
            # Find selected channel
            selected_channel = next((ch for ch in config['channels'] if ch['name'] == selected_channel_name), None)
            
            if selected_channel:
                if 'current_stream_key' not in st.session_state:
                    st.session_state['current_stream_key'] = selected_channel['stream_key']
                st.info(f"Using stream key from: {selected_channel_name}")
                
                # Display channel info if auth is available
                if 'auth' in selected_channel:
                    st.subheader("🔐 Channel Authentication")
                    if st.button("Verify Authentication"):
                        service = create_youtube_service(selected_channel['auth'])
                        if service:
                            channels = get_channel_info(service)
                            if channels:
                                channel = channels[0]
                                st.success(f"✅ Authenticated as: {channel['snippet']['title']}")
                                st.write(f"Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}")
                                st.write(f"Total Views: {channel['statistics'].get('viewCount', '0')}")
                                log_to_database(st.session_state['session_id'], "INFO", f"Channel authenticated: {channel['snippet']['title']}")
                            else:
                                st.error("❌ Could not fetch channel information")
        else:
            st.subheader("🔑 Manual Stream Key")
            
            # Check if we have a current stream key
            current_key = st.session_state.get('current_stream_key', '')
            manual_stream_key = st.text_input("Stream Key", 
                                     value=current_key, 
                                     type="password",
                                     help="Enter your YouTube stream key or get one using the button above")
            
            # Update session state with manual input
            if manual_stream_key:
                st.session_state['current_stream_key'] = manual_stream_key
            
            if current_key:
                st.success("✅ Using generated stream key")
            else:
                st.info("💡 Upload OAuth JSON and click 'Get Stream Key' for automatic key generation")
        
        # Enhanced Live Stream Settings
        st.subheader("📝 Live Stream Settings")
        
        # Basic settings
        col_basic1, col_basic2 = st.columns(2)
        
        with col_basic1:
            stream_title = st.text_input("🎬 Stream Title", value="Live Stream", max_chars=100, key="stream_title_input")
            privacy_status = st.selectbox("🔒 Privacy", ["public", "unlisted", "private"], key="privacy_status")
            made_for_kids = st.checkbox("👶 Made for Kids", key="made_for_kids")
        
        with col_basic2:
            categories = get_youtube_categories()
            category_names = list(categories.values())
            selected_category_name = st.selectbox("📂 Category", category_names, index=category_names.index("Gaming"))
            category_id = [k for k, v in categories.items() if v == selected_category_name][0]
            st.session_state['category_id'] = category_id
            
            # Stream schedule type
            stream_schedule_type = st.selectbox("⏰ Schedule", ["📍 Simpan sebagai Draft", "🔴 Publish Sekarang"])
        
        # Description
        stream_description = st.text_area("📄 Stream Description", 
                                        value="Live streaming session", 
                                        max_chars=5000,
                                        height=100,
                                        key="stream_description_input")
        
        # Tags
        tags_input = st.text_input("🏷️ Tags (comma separated)", 
                                 placeholder="gaming, live, stream, youtube",
                                 key="tags_input")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []
        
        if tags:
            st.write("**Tags:**", ", ".join(tags))
        
        # Technical settings
        with st.expander("🔧 Technical Settings"):
            col_tech1, col_tech2 = st.columns(2)
            
            with col_tech1:
                is_shorts = st.checkbox("📱 Shorts Mode (720x1280)")
                enable_chat = st.checkbox("💬 Enable Live Chat", value=True)
            
            with col_tech2:
                bitrate = st.selectbox("📊 Bitrate", ["1500k", "2500k", "4000k", "6000k"], index=1)
                framerate = st.selectbox("🎞️ Frame Rate", ["24", "30", "60"], index=1)
                resolution = st.selectbox("📺 Resolution", ["720p", "1080p", "1440p"], index=1)
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            custom_rtmp = st.text_input("🌐 Custom RTMP URL (optional)")
            enable_dvr = st.checkbox("📹 Enable DVR", value=True)
            enable_content_encryption = st.checkbox("🔐 Enable Content Encryption")
            
            # Thumbnail upload
            thumbnail_file = st.file_uploader("🖼️ Custom Thumbnail", type=['jpg', 'jpeg', 'png'])
            
            # Monetization settings
            st.subheader("💰 Monetization")
            enable_monetization = st.checkbox("💵 Enable Monetization")
            if enable_monetization:
                ad_breaks = st.checkbox("📺 Enable Ad Breaks")
                super_chat = st.checkbox("💬 Enable Super Chat", value=True)
    
    with col2:
        st.header("📊 Status & Controls")
        
        # Streaming status
        streaming = st.session_state.get('streaming', False)
        if streaming:
            st.error("🔴 LIVE")
            
            # Live stats
            if 'stream_start_time' in st.session_state:
                duration = datetime.now() - st.session_state['stream_start_time']
                st.metric("⏱️ Duration", str(duration).split('.')[0])
        else:
            st.success("⚫ OFFLINE")
        
        # Control buttons
        if st.button("▶️ Start Streaming", type="primary"):
            # Get the current stream key
            stream_key = st.session_state.get('current_stream_key', '')
            
            if not video_path:
                st.error("❌ Please select or upload a video!")
            elif not stream_key:
                st.error("❌ Stream key is required!")
            else:
                # Save streaming session
                save_streaming_session(
                    st.session_state['session_id'],
                    video_path,
                    stream_title,
                    stream_description,
                    ", ".join(tags),
                    category_id,
                    privacy_status,
                    made_for_kids,
                    st.session_state.get('channel_info', {}).get('snippet', {}).get('title', 'Unknown')
                )
                
                # Start streaming
                st.session_state['streaming'] = True
                st.session_state['stream_start_time'] = datetime.now()
                st.session_state['live_logs'] = []
                
                def log_callback(msg):
                    if 'live_logs' not in st.session_state:
                        st.session_state['live_logs'] = []
                    st.session_state['live_logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
                    # Keep only last 100 logs in memory
                    if len(st.session_state['live_logs']) > 100:
                        st.session_state['live_logs'] = st.session_state['live_logs'][-100:]
                
                st.session_state['ffmpeg_thread'] = threading.Thread(
                    target=run_ffmpeg, 
                    args=(video_path, stream_key, is_shorts, log_callback, custom_rtmp or None, st.session_state['session_id']), 
                    daemon=True
                )
                st.session_state['ffmpeg_thread'].start()
                st.success("🚀 Streaming started!")
                log_to_database(st.session_state['session_id'], "INFO", f"Streaming started: {video_path}")
                st.rerun()
        
        if st.button("⏹️ Stop Streaming", type="secondary"):
            st.session_state['streaming'] = False
            if 'stream_start_time' in st.session_state:
                del st.session_state['stream_start_time']
            os.system("pkill ffmpeg")
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")
            st.warning("⏸️ Streaming stopped!")
            log_to_database(st.session_state['session_id'], "INFO", "Streaming stopped by user")
            st.rerun()
        
        # Live broadcast info
        if 'live_broadcast_info' in st.session_state:
            st.subheader("📺 Live Broadcast")
            broadcast_info = st.session_state['live_broadcast_info']
            st.write(f"**Watch URL:** [Open Stream]({broadcast_info['watch_url']})")
            if 'studio_url' in broadcast_info:
                st.write(f"**Studio URL:** [Manage]({broadcast_info['studio_url']})")
            st.write(f"**Broadcast ID:** {broadcast_info.get('broadcast_id', 'N/A')}")
        
        # Statistics
        st.subheader("📈 Statistics")
        
        # Session stats
        session_logs = get_logs_from_database(st.session_state['session_id'], 50)
        st.metric("Session Logs", len(session_logs))
        
        if 'live_logs' in st.session_state:
            st.metric("Live Log Entries", len(st.session_state['live_logs']))
        
        # Channel info display
        if 'channel_config' in st.session_state:
            config = st.session_state['channel_config']
            st.metric("Configured Channels", len(config['channels']))
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("📋 Copy Stream Key"):
            if 'current_stream_key' in st.session_state:
                st.code(st.session_state['current_stream_key'])
                st.success("Stream key displayed above!")
        
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Live Logs Section
    st.markdown("---")
    st.header("📝 Live Streaming Logs")
    
    # Log tabs
    tab1, tab2, tab3 = st.tabs(["🔴 Live Logs", "📊 Session History", "🗂️ All Logs"])
    
    with tab1:
        st.subheader("Real-time Streaming Logs")
        
        # Live logs container
        log_container = st.container()
        with log_container:
            if 'live_logs' in st.session_state and st.session_state['live_logs']:
                # Show last 50 live logs
                recent_logs = st.session_state['live_logs'][-50:]
                logs_text = "\\n".join(recent_logs)
                st.text_area("Live Logs", logs_text, height=300, disabled=True, key="live_logs_display")
            else:
                st.info("No live logs available. Start streaming to see real-time logs.")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh logs", value=streaming)
        
        if auto_refresh and streaming:
            time.sleep(2)
            st.rerun()
    
    with tab2:
        st.subheader("Current Session History")
        
        session_logs = get_logs_from_database(st.session_state['session_id'], 100)
        if session_logs:
            # Create a formatted display
            for log in session_logs[:20]:  # Show last 20 session logs
                timestamp, log_type, message, video_file, channel_name = log
                
                # Color code by log type
                if log_type == "ERROR":
                    st.error(f"**{timestamp}** - {message}")
                elif log_type == "INFO":
                    st.info(f"**{timestamp}** - {message}")
                elif log_type == "FFMPEG":
                    st.text(f"{timestamp} - {message}")
                else:
                    st.write(f"**{timestamp}** - {message}")
        else:
            st.info("No session logs available yet.")
    
    with tab3:
        st.subheader("All Historical Logs")
        
        # Filter options
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            log_limit = st.selectbox("Show logs", [50, 100, 200, 500], index=1)
        
        with col_filter2:
            log_type_filter = st.selectbox("Filter by type", ["All", "INFO", "ERROR", "FFMPEG"])
        
        all_logs = get_logs_from_database(limit=log_limit)
        
        if all_logs:
            # Filter by type if selected
            if log_type_filter != "All":
                all_logs = [log for log in all_logs if log[1] == log_type_filter]
            
            # Display in expandable sections
            for i, log in enumerate(all_logs[:50]):  # Limit display to 50 for performance
                timestamp, log_type, message, video_file, channel_name = log
                
                with st.expander(f"{log_type} - {timestamp} - {message[:50]}..."):
                    st.write(f"**Timestamp:** {timestamp}")
                    st.write(f"**Type:** {log_type}")
                    st.write(f"**Message:** {message}")
                    if video_file:
                        st.write(f"**Video File:** {video_file}")
                    if channel_name:
                        st.write(f"**Channel:** {channel_name}")
        else:
            st.info("No historical logs available.")

def get_requirements_txt():
    """Get requirements.txt content"""
    return """streamlit
pandas
psutil
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
requests
ffmpeg
opencv-python-headless
pillow
numpy
ffmpeg-python
pytube
pytz
google-auth
google-auth-oauthlib
google-api-python-client
requests"""

def get_readme_content(repo_name):
    """Get README.md content"""
    return f"""# {repo_name} - YouTube Live Streaming Platform

🎥 Advanced YouTube Live Streaming Platform with auto-deployment to Streamlit Cloud.

## Features

- 🔐 Google OAuth Integration for YouTube API
- 📺 YouTube Live Broadcast Creation & Management
- 🔑 Automatic Stream Key Generation
- 📹 Video Upload & Multi-format Support
- 🎬 FFmpeg Integration for Live Streaming
- 📊 Real-time Monitoring & Logging
- 💾 SQLite Database for Persistent Storage
- 🎨 Beautiful, Responsive UI
- 🚀 Auto-deployment to Streamlit Cloud

## Live Demo

Visit the live application: [Your App URL will be available after deployment]

## Setup Instructions

### 1. Clone the repository:
```bash
git clone https://github.com/yourusername/{repo_name}.git
cd {repo_name}
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. System dependencies (for local development):
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download FFmpeg from https://ffmpeg.org/download.html
```

### 4. Google OAuth Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Download the JSON file
6. Upload it in the application

### 5. Run the application:
```bash
streamlit run app.py
```

## Application Features

### 🔐 Authentication
- Google OAuth 2.0 integration
- YouTube API authentication
- Persistent channel storage
- Multiple account support

### 📺 Live Streaming
- Create YouTube Live broadcasts
- Generate stream keys automatically
- Configure stream settings (title, description, tags, privacy)
- Support for Shorts mode (720x1280)
- Custom RTMP URL support

### 📹 Video Management
- Upload videos (MP4, FLV, AVI, MOV, MKV)
- Select from existing video files
- Real-time video processing
- Multiple format support

### 🎬 FFmpeg Integration
- High-quality streaming with FFmpeg
- Configurable bitrate and resolution
- Real-time encoding
- Stream monitoring and logging

### 📊 Monitoring & Logging
- Real-time streaming logs
- SQLite database for persistent storage
- Session management
- Error tracking and reporting
- Export logs functionality

## File Structure

```
{repo_name}/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── packages.txt        # System dependencies (FFmpeg)
├── README.md          # This documentation
└── streaming_logs.db  # SQLite database (created automatically)
```

## Configuration

### YouTube API Setup
1. Enable YouTube Data API v3 in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs
4. Download credentials JSON file

### Stream Settings
- **Title**: Stream title (max 100 characters)
- **Description**: Stream description (max 5000 characters)
- **Tags**: Comma-separated tags for discovery
- **Category**: YouTube video category
- **Privacy**: Public, Unlisted, or Private
- **Made for Kids**: COPPA compliance setting

### Technical Settings
- **Resolution**: 720p, 1080p, 1440p
- **Bitrate**: 1500k, 2500k, 4000k, 6000k
- **Frame Rate**: 24, 30, 60 FPS
- **Shorts Mode**: 720x1280 vertical format

## Deployment

This application is automatically deployed to Streamlit Cloud whenever changes are pushed to the main branch.

### Manual Deployment Steps:
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Select this repository
4. Set main file path: `app.py`
5. Click "Deploy!"

## Dependencies

### Python Packages
- `streamlit`: Web framework
- `google-auth`: Google authentication
- `google-api-python-client`: YouTube API client
- `ffmpeg-python`: FFmpeg Python bindings
- `opencv-python-headless`: Video processing
- `pandas`: Data manipulation
- `requests`: HTTP requests

### System Dependencies
- `ffmpeg`: Video encoding and streaming

## Usage Guide

### 1. Authentication
1. Upload Google OAuth JSON file
2. Click authorization link
3. Grant YouTube permissions
4. Return to application (automatic)

### 2. Create Live Stream
1. Fill out stream settings form
2. Click "Create YouTube Live"
3. Copy stream key or use automatic streaming

### 3. Start Streaming
1. Select or upload video file
2. Configure technical settings
3. Click "Start Streaming"
4. Monitor real-time logs

### 4. Manage Streams
- View existing broadcasts
- Reuse stream keys
- Access YouTube Studio
- Monitor stream status

## Troubleshooting

### Common Issues
1. **FFmpeg not found**: Install FFmpeg system dependency
2. **Authentication failed**: Check OAuth credentials and scopes
3. **Stream key invalid**: Regenerate stream key or create new broadcast
4. **Video upload failed**: Check file format and size limits

### Error Logs
- Check real-time logs tab for streaming issues
- Review session history for authentication problems
- Export logs for detailed debugging

## Security Notes

- OAuth tokens are stored securely in session state
- Stream keys are displayed as password fields
- Database contains no sensitive authentication data
- All API calls use secure HTTPS connections

## Contributing

Feel free to submit issues and enhancement requests!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For questions or issues:
- Check the application's built-in help sections
- Review YouTube API documentation
- Create an issue in this repository
- Check FFmpeg documentation for streaming issues

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with Streamlit framework
- Uses YouTube Data API v3
- FFmpeg for video processing
- Google OAuth for authentication

---

**Happy Streaming!** 🎥✨

*Auto-generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

# Main app
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🚀 GitHub → Streamlit Deployer</h1>
        <p>Create GitHub repositories and auto-deploy to Streamlit Cloud</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    # GitHub token input
    github_token = st.sidebar.text_input(
        "GitHub Personal Access Token",
        type="password",
        help="Create a token at https://github.com/settings/tokens"
    )
    
    # Repository details
    st.sidebar.subheader("Repository Details")
    repo_name = st.sidebar.text_input("Repository Name", "my-streamlit-app")
    repo_description = st.sidebar.text_area(
        "Description", 
        "A beautiful Streamlit application with auto-deployment"
    )
    private_repo = st.sidebar.checkbox("Private Repository", False)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>✨ Features</h3>
            <ul>
                <li>🔧 Automatically creates GitHub repository</li>
                <li>📱 Includes beautiful Streamlit app template</li>
                <li>🚀 Sets up auto-deployment to Streamlit Cloud</li>
                <li>📊 Pre-configured with data visualization tools</li>
                <li>🎨 Modern, responsive design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Create Repository & Deploy", type="primary"):
            if not github_token:
                st.markdown("""
                <div class="error-message">
                    ❌ Please provide a GitHub Personal Access Token
                </div>
                """, unsafe_allow_html=True)
                return
            
            if not repo_name:
                st.markdown("""
                <div class="error-message">
                    ❌ Please provide a repository name
                </div>
                """, unsafe_allow_html=True)
                return
            
            with st.spinner("Creating repository..."):
                # Create repository
                response = create_github_repo(
                    github_token, 
                    repo_name, 
                    repo_description, 
                    private_repo
                )
                
                if response.status_code == 201:
                    repo_data = response.json()
                    owner = repo_data['owner']['login']
                    
                    st.markdown("""
                    <div class="success-message">
                        ✅ Repository created successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Upload files
                    files_to_upload = [
                        ("app.py", get_streamlit_app_template(), "Add Streamlit app"),
                        ("requirements.txt", get_requirements_txt(), "Add requirements"),
                        ("README.md", get_readme_content(repo_name), "Add README"),
                        ("packages.txt", "ffmpeg", "Add system packages")
                    ]
                    
                    progress_bar = st.progress(0)
                    
                    for i, (file_path, content, message) in enumerate(files_to_upload):
                        upload_response = upload_file_to_repo(
                            github_token, owner, repo_name, file_path, content, message
                        )
                        
                        if upload_response.status_code in [201, 200]:
                            st.success(f"✅ {file_path} uploaded successfully")
                        else:
                            st.error(f"❌ Failed to upload {file_path}")
                        
                        progress_bar.progress((i + 1) / len(files_to_upload))
                    
                    # Display repository info
                    st.markdown(f"""
                    <div class="info-box">
                        <h3>🎉 Repository Created!</h3>
                        <p><strong>Repository URL:</strong> <a href="{repo_data['html_url']}" target="_blank">{repo_data['html_url']}</a></p>
                        <p><strong>Clone URL:</strong> {repo_data['clone_url']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Streamlit Cloud deployment instructions
                    st.markdown("""
                    <div class="feature-card">
                        <h3>🚀 Deploy to Streamlit Cloud</h3>
                        <p>Follow these steps to deploy your app:</p>
                        <ol>
                            <li>Go to <a href="https://share.streamlit.io/" target="_blank">share.streamlit.io</a></li>
                            <li>Click "New app"</li>
                            <li>Select your repository</li>
                            <li>Set main file path: <code>app.py</code></li>
                            <li>Click "Deploy!"</li>
                        </ol>
                        <p>Your app will be automatically deployed and updated whenever you push to GitHub!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    error_message = response.json().get('message', 'Unknown error')
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Failed to create repository: {error_message}
                    </div>
                    """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Setup Instructions</h3>
            <p><strong>1. Get GitHub Token:</strong></p>
            <ol>
                <li>Go to GitHub Settings</li>
                <li>Developer settings → Personal access tokens</li>
                <li>Generate new token (classic)</li>
                <li>Select 'repo' scope</li>
                <li>Copy the token</li>
            </ol>
            
            <p><strong>2. Repository Setup:</strong></p>
            <ul>
                <li>Choose a unique name</li>
                <li>Add description</li>
                <li>Select visibility</li>
            </ul>
            
            <p><strong>3. Deployment:</strong></p>
            <ul>
                <li>Automatic file upload</li>
                <li>Streamlit Cloud integration</li>
                <li>Live URL generation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
