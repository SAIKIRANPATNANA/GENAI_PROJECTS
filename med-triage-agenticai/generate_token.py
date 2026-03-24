import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def is_web_credentials(credentials_path):
    """Check if the credentials are for a web app or desktop app"""
    try:
        with open(credentials_path, 'r') as file:
            data = json.load(file)
            return 'web' in data
    except:
        return False

def main():
    creds = None
    credentials_file = 'credentials.json'
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None
        
        if not creds:
            # Check if we're dealing with web credentials
            is_web = is_web_credentials(credentials_file)
            
            if is_web:
                print("Detected web application credentials. Using specific redirect URI.")
                
                # For web credentials, we need to use a specific redirect URI
                # This is a workaround using manual authorization
                try:
                    # Read the credentials file
                    with open(credentials_file, 'r') as file:
                        client_config = json.load(file)
                    
                    # Create a flow using the web client config but specifying the redirect URI
                    flow = Flow.from_client_config(
                        client_config,
                        scopes=SCOPES,
                        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Special URI for manual auth
                    )
                    
                    # Generate the authorization URL
                    auth_url, _ = flow.authorization_url(
                        access_type='offline',
                        include_granted_scopes='true',
                        prompt='consent'
                    )
                    
                    print("\n⚠️ You need to authorize this application.")
                    print(f"\n1. Visit this URL in your browser: \n\n{auth_url}\n")
                    print("2. Sign in and authorize the application")
                    print("3. Copy the authorization code you receive")
                    
                    # Get the authorization code from the user
                    code = input("\nEnter the authorization code: ").strip()
                    
                    # Exchange the code for credentials
                    flow.fetch_token(code=code)
                    
                    # Get the credentials
                    creds = flow.credentials
                    
                except Exception as e:
                    print(f"❌ Manual authorization failed: {e}")
                    print("\nPlease try again or create desktop application credentials.")
                    return
            else:
                # For desktop/installed app credentials
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, 
                        SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"❌ Local server authentication failed: {e}")
                    print("Please create proper OAuth credentials in Google Cloud Console.")
                    print("See: https://developers.google.com/calendar/api/quickstart/python")
                    return
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    print("✅ Authentication successful! Token saved to token.pickle.")
    
    # Verify the token works by making a simple API call
    try:
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        calendars = service.calendarList().list().execute()
        print(f"✅ Successfully verified access to {len(calendars.get('items', []))} calendars")
    except Exception as e:
        print(f"❌ Error verifying calendar access: {e}")

if __name__ == '__main__':
    main()