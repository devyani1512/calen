from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dateparser import parse
import json

def get_service(user):
    print("🔍 user.auth_info = ", user.auth_info)  # 👈 Add this
    info = json.loads(user.auth_info)
    creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=creds)




def handle_calendar_command(command, user):
    service = get_service(user)
    # Dummy response for now, you can expand this
    return "📅 Calendar feature under construction."
