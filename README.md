# AI-Powered Calendar Assistant

A voice-enabled web assistant that helps users manage their Google Calendar through natural language input. Built with GPT-4 Function Calling and Google Calendar API, it supports adding, retrieving, and deleting calendar events—securely scoped for each user via OAuth2 authentication.

## Features

- Voice and text-based calendar interaction
- Natural language understanding using GPT-4 Function Calling
- Integration with Google Calendar for real-time event operations
- Secure user login using OAuth2 (per-user access control)
- Lightweight frontend built with HTML, CSS, and JavaScript
- Text-to-speech support for assistant responses
- Designed for multi-user workflows

## Tech Stack

| Layer      | Tools & Technologies                       |
|------------|--------------------------------------------|
| Backend    | Python, Flask                              |
| AI Engine  | OpenAI GPT-4 Function Calling              |
| Calendar   | Google Calendar API                        |
| Auth       | OAuth 2.0 (Google Client-Based Login)      |
| Frontend   | HTML5, CSS3, JavaScript                    |
| Hosting    |  Render                                    |
| Extras     | Web Speech API, pyngrok (for testing)      |

## Project Structure

```
calendar-assistant/
├── app.py
├── models.py
├── utils.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── .env
└── requirements.txt
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/devyani1512/calen.git
cd calen
```

### 2. Configure Environment Variables
Create a `.env` file with:
```
FLASK_ENV=development
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
CLIENT_ID=your_google_client_id
CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=http://localhost:5000/callback
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Locally
```bash
flask run
```
Then visit: [http://localhost:5000](http://localhost:5000)

## Sample Screens

| Login Interface          | Query Panel              |
|--------------------------|--------------------------|
| ![Login](screenshots/login.png) | ![Query](screenshots/query.png) |

## Prompt Workflow

```
User input: "Add a team sync next Monday at 10AM"
↓
Parsed by GPT-4 → {function_call: create_event, data: {...}}
↓
Flask backend routes to Google Calendar API
↓
Calendar updated
↓
User receives text and optional voice confirmation
```

## OAuth 2.0 Integration

The assistant uses Google’s OAuth 2.0 login (not a service account), enabling secure, user-specific access. Each user logs in and grants calendar permissions—only their calendar is accessible.

## Status

- Working MVP with live calendar updates
- Voice-enabled interface operational
- Ongoing improvements for token management and UI polish

## Resources

- GitHub: [https://github.com/devyani1512/calen](https://github.com/devyani1512/calen)
- Optional Live Demo: [https://calen-o3rg.onrender.com/](https://calen-o3rg.onrender.com/)

## License

MIT License  
© 2025 Devyani Sharma
