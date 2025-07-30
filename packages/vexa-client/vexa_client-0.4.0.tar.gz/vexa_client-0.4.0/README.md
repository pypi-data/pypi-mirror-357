# Vexa Client Python

🚀 **Build Meeting Assistants in Hours, Not Months**

A Python client library for **Vexa** - the privacy-first, open-source API for **real-time meeting transcription**. Build powerful meeting assistants with just a few lines of code.


- 🤖 **Meeting Bots**: Send bots to automatically join Google Meet, (Zoom, Teams coming soon)
- 🌍 **109 Languages**: Real-time transcription and translation across all of them  
- 🧠 **Auto Language Detection**: No language setup needed - Vexa automatically detects what's being spoken
- 🔄 **Real-time Translation**: Choose any target language for instant translation instead of transcription
- ⚡ **Real-time**: Get transcripts as meetings happen, not after
- 🔔 **Webhook Automation**: Get notified instantly when meetings end for seamless post-meeting workflows
- 🔒 **Privacy-First**: Open-source alternative to recall.ai - your data stays under your control
- 🚀 **Rapid Development**: Build complex meeting apps in hours 
- 🎯 **Simple API**: Clean abstractions that make building on top a joy

## What You Can Build

Transform your ideas into reality with Vexa's powerful API:

- **Meeting Assistant Apps**: Like Otter.ai, Fireflies.ai, Fathom
- **CRM Integrations**: Auto-populate meeting notes in Salesforce, HubSpot
- **Compliance Tools**: Automatically record and transcribe important business calls
- **Language Learning**: Real-time translation for international meetings
- **Accessibility Tools**: Live captions for hearing-impaired participants
- **Analytics Dashboards**: Extract insights from meeting conversations

## Core Features

- **🤖 Bot Management**: Start, stop, and configure transcription bots for meetings
- **📝 Real-time Transcription**: Access meeting transcripts as they happen  
- **🔔 Webhook Support**: Get real-time notifications when transcripts are ready
- **🌐 Multi-language**: Support for 99 languages with instant translation
- **🔧 Admin Tools**: Manage users and API tokens (for self-hosted deployments)
- **🛡️ Type Safety**: Full type annotation support for better IDE integration
- **⚠️ Error Handling**: Comprehensive error handling with custom exceptions

## API Operations Overview

**🎯 User Operations**: These are the primary operations for API users who want to integrate Vexa's transcription capabilities into their applications. This includes bot management, accessing transcripts, and configuring webhooks.

**🔧 Admin Operations (Self-hosting only)**: These operations are exclusively for users who self-host Vexa and need to manage user accounts, create API tokens, and perform administrative tasks. Most API users will not need these operations.

## Get Started in 5 Minutes

### 1. Get Your API Key
Get your API key in 3 clicks at [www.vexa.ai](https://www.vexa.ai) - no waiting, no approval process!

### 2. Install the Client
```bash
pip install vexa-client
```

### 3. Start Building
```python
from vexa_client import VexaClient

# You're ready to build!
client = VexaClient(api_key="your-api-key-here")
```

## Installation Options

### From PyPI (Recommended)
```bash
pip install vexa-client
```

### From Source
```bash
git clone https://github.com/vexa/vexa-client-python.git
cd vexa-client-python
pip install -e .
```

## Quick Start Example

```python
from vexa_client import VexaClient

# Initialize the client
client = VexaClient(
    base_url="https://gateway.dev.vexa.ai",  # Default Vexa API Gateway URL
    api_key="your-api-key-here",            # For user operations
    admin_key="your-admin-key-here"         # For admin operations (self-hosting only)
)

# Request a bot to join a meeting
meeting = client.request_bot(
    platform="google_meet",
    native_meeting_id="abc-def-ghi",
    bot_name="Vexa Bot",
    language="en"  # Optional - auto-detected if not provided
)

# Get running bots status
bots = client.get_running_bots_status()
print(f"Running bots: {len(bots)}")

# Retrieve meetings
meetings = client.get_meetings()
for meeting in meetings:
    print(f"Meeting: {meeting['platform']} - {meeting['status']}")

# Get transcript for a specific meeting
transcript = client.get_transcript("google_meet", "abc-def-ghi")
```

## Real-World Example: Build a Meeting Summary Bot

Here's a complete example showing how to build a meeting summary bot:

```python
from vexa_client import VexaClient
import time

# Initialize client
client = VexaClient(api_key="your-api-key-here")

# 1. Send bot to join a meeting
meeting = client.request_bot(
    platform="google_meet",
    native_meeting_id="abc-def-ghi",
    bot_name="Summary Bot",
    language="en"
)
print(f"Bot joined meeting: {meeting['id']}")

# 2. Wait for meeting to complete or set up webhook to get notified

# 3. Get the transcript
transcript = client.get_transcript("google_meet", "abc-def-ghi")

# 4. Process transcript into summary
transcripts = transcript['data']['transcripts']
speakers = set(t['speaker'] for t in transcripts)
meeting_length = len(transcripts)

print(f"Meeting Summary:")
print(f"- Participants: {', '.join(speakers)}")
print(f"- Duration: {meeting_length} segments")
print(f"- First topic: {transcripts[0]['text']}")

# 5. Update meeting with metadata
client.update_meeting_data(
    platform="google_meet",
    native_meeting_id="abc-def-ghi",
    name="Weekly Team Standup",
    participants=list(speakers),
    notes="Auto-generated summary available"
)
```

**That's it!** You just built a functional meeting bot that can:
- Join meetings automatically
- Transcribe in real-time across 99 languages
- Extract participant information
- Generate meeting summaries
- Store metadata for later retrieval

## Language Detection & Translation Workflows

### Auto Language Detection
```python
# No language specified - Vexa automatically detects what's being spoken
meeting = client.request_bot(
    platform="google_meet",
    native_meeting_id="abc-def-ghi",
    bot_name="Smart Bot"
    # language not specified - auto-detection enabled!
)
```

### 📝 Transcription in Specific Language
```python
# Transcribe in specific language (if you know what will be spoken)
meeting = client.request_bot(
    platform="google_meet",
    native_meeting_id="abc-def-ghi",
    language="es",  # Spanish transcription
    task="transcribe"
)
```

## 🔔 Webhook Automation for Post-Meeting Workflows

Set up webhooks to get notified instantly when meetings end - perfect for automated post-meeting processing:

### Step 1: Set Your Webhook URL
```python
# Set up webhook to receive meeting completion notifications
client.set_webhook_url("https://your-server.com/webhook/vexa")
```

### Step 2: Handle Webhook Notifications
```python
# Your webhook endpoint receives this when a meeting ends:
# POST https://your-server.com/webhook/vexa
# {
#   "event": "meeting.completed",
#   "meeting_id": "abc-def-ghi",
#   "platform": "google_meet",
#   "status": "completed",
#   "timestamp": "2024-01-15T10:30:00Z"
# }
```

### Step 3: Automated Post-Meeting Processing
```python
from flask import Flask, request
app = Flask(__name__)

@app.route('/webhook/vexa', methods=['POST'])
def handle_meeting_completion():
    data = request.json
    
    if data['event'] == 'meeting.completed':
        # Meeting just ended - fetch transcript immediately!
        transcript = client.get_transcript(
            platform=data['platform'],
            native_meeting_id=data['meeting_id']
        )
        
        # Now you can:
        # - Send summary emails
        # - Update CRM records
        # - Generate action items
        # - Trigger other automations
        
        process_meeting_transcript(transcript)
    
    return {"status": "received"}

def process_meeting_transcript(transcript):
    # Your custom post-meeting automation here
    print(f"Processing {len(transcript['data']['transcripts'])} transcript segments")
    # Send to your CRM, email summaries, extract action items, etc.
```

**💡 Why Webhooks Are Powerful:**
- ⚡ **Instant Processing**: No polling needed - get notified the moment meetings end
- 🤖 **Full Automation**: Build completely hands-off meeting workflows
- 🔄 **Reliable**: Never miss a meeting completion event
- 📈 **Scalable**: Handle hundreds of concurrent meetings effortlessly

## API Reference

### Bot Management

#### `request_bot(platform, native_meeting_id, bot_name=None, language=None, task=None)`
Request a new bot to join a meeting.

**Parameters:**
- `platform` (str): Platform identifier (e.g., 'google_meet', 'zoom')
- `native_meeting_id` (str): Platform-specific meeting identifier
- `bot_name` (str, optional): Name for the bot in the meeting
- `language` (str, optional): Language code (e.g., 'en', 'es', 'fr'). **If not provided, Vexa automatically detects the spoken language**
- `task` (str, optional): Choose workflow:
  - `'transcribe'` (default): Get transcription in the detected/specified language
  - `'translate'`: Get real-time translation to the target language specified in `language` parameter

**Language Workflows:**
```python
# Auto-detect language (recommended)
client.request_bot("google_meet", "meeting-id")

# Transcribe in specific language  
client.request_bot("google_meet", "meeting-id", language="es", task="transcribe")

# Translate everything to English
client.request_bot("google_meet", "meeting-id", language="en", task="translate")
```

#### `stop_bot(platform, native_meeting_id)`
Stop a running bot for a specific meeting.

#### `update_bot_config(platform, native_meeting_id, language=None, task=None)`
Update the configuration of an active bot.

#### `get_running_bots_status()`
Get the status of all running bot containers for the authenticated user.

### Transcriptions and Meetings

#### `get_meetings()`
Retrieve the list of meetings initiated by the user.

#### `get_meeting_by_id(platform, native_meeting_id)`
Retrieve a specific meeting by platform and native ID.

#### `get_transcript(platform, native_meeting_id)`
Retrieve the transcript for a specific meeting.

#### `update_meeting_data(platform, native_meeting_id, name=None, participants=None, languages=None, notes=None)`
Update meeting metadata.

#### `delete_meeting(platform, native_meeting_id)`
Delete a meeting and all its associated transcripts.

### User Profile

#### `set_webhook_url(webhook_url)`
Set the webhook URL for the authenticated user.

### Admin Operations (Self-hosting Only)

> ⚠️ **Note**: Admin operations are only available for self-hosted Vexa deployments. Most API users (95%) will only need the User Operations above.

#### `create_user(email, name=None, image_url=None, max_concurrent_bots=None)`
Create a new user (Self-hosting admin only).

#### `list_users(skip=0, limit=100)`
List users in the system (Self-hosting admin only).

#### `update_user(user_id, name=None, image_url=None, max_concurrent_bots=None)`
Update user information (Self-hosting admin only).

#### `get_user_by_email(email)`
Retrieve a user by email address (Self-hosting admin only).

#### `create_token(user_id)`
Generate a new API token for a user (Self-hosting admin only).

## Configuration

The client can be configured with environment variables:

```bash
export VEXA_BASE_URL="https://gateway.dev.vexa.ai"
export VEXA_API_KEY="your-api-key"
export VEXA_ADMIN_KEY="your-admin-key"  # Only needed for self-hosting
```

```python
import os
from vexa_client import VexaClient

client = VexaClient(
    base_url=os.getenv("VEXA_BASE_URL", "https://gateway.dev.vexa.ai"),
    api_key=os.getenv("VEXA_API_KEY"),
    admin_key=os.getenv("VEXA_ADMIN_KEY")  # Only needed for self-hosting
)
```

## Error Handling

The client raises `VexaClientError` for API-related errors:

```python
from vexa_client import VexaClient, VexaClientError

try:
    client = VexaClient(api_key="invalid-key")
    meetings = client.get_meetings()
except VexaClientError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Examples

### Managing Meeting Bots

```python
# Start a bot for a Google Meet
meeting = client.request_bot(
    platform="google_meet",
    native_meeting_id="abc-def-ghi",
    bot_name="Meeting Recorder",
    language="en",
    task="transcribe"
)

# Update bot configuration during the meeting
client.update_bot_config(
    platform="google_meet",
    native_meeting_id="abc-def-ghi",
    language="es"  # Switch to Spanish
)

# Stop the bot when done
result = client.stop_bot("google_meet", "abc-def-ghi")
print(result["message"])
```

### Working with Transcripts

```python
# Get all meetings
meetings = client.get_meetings()

for meeting in meetings:
    if meeting["status"] == "completed":
        # Get transcript
        transcript = client.get_transcript(
            meeting["platform"], 
            meeting["native_meeting_id"]
        )
        
        # Update meeting metadata
        client.update_meeting_data(
            meeting["platform"],
            meeting["native_meeting_id"],
            name="Weekly Team Standup",
            notes="Discussed project milestones and blockers"
        )
```

### Admin Operations (Self-hosting Only)

> ⚠️ **Note**: These examples are only for self-hosted Vexa deployments.

```python
# Create a new user (self-hosting only)
user = client.create_user(
    email="newuser@example.com",
    name="New User",
    max_concurrent_bots=3
)

# Generate API token for the user (self-hosting only)
token = client.create_token(user["id"])
print(f"New API token: {token['token']}")

# List all users (self-hosting only)
users = client.list_users(limit=50)
print(f"Total users: {len(users)}")
```

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Join the Vexa Community

🚀 **Help us reach 1000 stars!** Current: ![GitHub stars](https://img.shields.io/github/stars/Vexa-ai/vexa?style=social) → Goal: 1000 ⭐️

Join thousands of developers building the future of meeting intelligence:

- 💬 [Discord Community](https://discord.gg/Ga9duGkVz9) - Get help, share projects, connect with other builders
- 🌐 [Vexa Website](https://www.vexa.ai) - Get your API key and explore features
- 💼 [LinkedIn](https://www.linkedin.com/company/vexa-ai/) - Follow for updates and announcements
- 🐦 [X (@grankin_d)](https://x.com/grankin_d) - Connect with the founder

## What Developers Are Saying

> *"Built our meeting assistant MVP in 3 hours with Vexa. The API is incredibly clean and the real-time transcription is spot-on."* - Open Source Developer

> *"Finally, a privacy-first alternative to proprietary solutions. Perfect for our enterprise needs."* - Enterprise Developer

> *"The 99-language support is a game changer for our international team meetings."* - Startup Founder

## Support

For support and questions:

- 💬 [Discord Community](https://discord.gg/Ga9duGkVz9) - Fastest way to get help
- 📚 Documentation: https://docs.vexa.ai
- 🐛 Issues: https://github.com/vexa/vexa-client-python/issues
- ✉️ Email: support@vexa.ai

[![Join Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/Ga9duGkVz9) 