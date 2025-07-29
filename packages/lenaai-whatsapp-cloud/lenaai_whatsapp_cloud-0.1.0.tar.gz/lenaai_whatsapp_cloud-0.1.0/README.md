# WhatsApp Cloud API Integration

A multi-platform messaging API that integrates with WhatsApp Business API, Facebook Messenger, Telegram, and Twilio.

## 🚀 Quick Start

### Option 1: Using the launcher scripts (Recommended)
```bash
# Windows Batch
run.bat

# PowerShell
.\run.ps1
```

### Option 2: Manual start
```bash
# Activate environment
conda activate whatsapp_cloud_env

# Run from project root
python main.py
```

### Option 3: Using uvicorn directly
```bash
conda activate whatsapp_cloud_env
uvicorn src.app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📁 File Structure

```
whatsapp_cloud/
├── main.py                 # 🚀 Main entry point (run from here!)
├── run.bat                 # Windows batch launcher
├── run.ps1                 # PowerShell launcher
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── Dockerfile             # Docker configuration
├── README.md              # This file
├── SETUP_GUIDE.md         # Detailed setup instructions
└── src/                   # Source code
    ├── __init__.py        # Package initialization
    ├── app/               # FastAPI application
    │   ├── __init__.py
    │   ├── main.py        # FastAPI app definition
    │   └── routers/       # API route handlers
    │       ├── __init__.py
    │       ├── message_router.py
    │       ├── webhook_router.py
    │       └── send_sheet_router.py
    ├── utils/             # Utility functions
    │   ├── __init__.py
    │   ├── config.py      # Configuration management
    │   ├── model.py       # Data models
    │   └── ...
    ├── message_handler/   # Message sending handlers
    │   ├── __init__.py
    │   ├── base_message_handler.py
    │   ├── whatsapp_message_handler.py
    │   └── ...
    ├── webhook_handler/   # Webhook processing
    │   ├── __init__.py
    │   ├── base_webhook_handler.py
    │   └── ...
    ├── data_extractors/   # Google Sheets integration
    │   ├── __init__.py
    │   └── ...
    ├── whatsapp_sheet/    # WhatsApp bulk messaging
    │   ├── __init__.py
    │   └── ...
    ├── telegram_sheet/    # Telegram bulk messaging
    │   ├── __init__.py
    │   └── ...
    └── twilio_sheet/      # Twilio bulk messaging
        ├── __init__.py
        └── ...
```

## 🎯 Key Features

- **Multi-platform messaging**: WhatsApp, Messenger, Telegram, Twilio
- **Webhook processing**: Handle incoming messages from all platforms
- **Bulk messaging**: Send messages to multiple recipients using Google Sheets
- **AI integration**: Connect with Lena AI for intelligent responses
- **Media support**: Send images, videos, and voice messages
- **Multi-client support**: Handle multiple business accounts

## 🌐 API Endpoints

### Health Check
- `GET /` - Server status

### Message Sending
- `POST /message/multi-platform/text` - Send text messages
- `POST /message/multi-platform/images` - Send images
- `POST /message/multi-platform/video` - Send videos

### Webhooks
- `POST /webhook-whatsapp` - WhatsApp incoming messages
- `POST /webhook-messenger` - Facebook Messenger messages
- `POST /telegram-webhook/{bot_token}` - Telegram messages
- `POST /webhook-twilio` - Twilio WhatsApp messages

### Bulk Messaging
- `POST /send-video-using-spreadsheet-whatsapp` - WhatsApp bulk video
- `POST /send-telegram-message-using-spreadsheet` - Telegram bulk messages
- `POST /send-video-using-spreadsheet` - Twilio bulk media

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Fill in your API credentials
3. Set `LOCAL_ENV=True` for local development

See `SETUP_GUIDE.md` for detailed configuration instructions.

## 🐳 Docker

```bash
# Build and run with Docker
docker build -t whatsapp-cloud-api .
docker run -p 8001:80 whatsapp-cloud-api
```

## 📚 Documentation

- **API Docs**: http://localhost:8001/docs (when server is running)
- **Setup Guide**: See `SETUP_GUIDE.md`
- **Environment Variables**: See `.env` file

## 🚨 Important Notes

- **Always run from project root**: `python main.py` (not from `src/app/`)
- **Use launcher scripts**: `run.bat` or `run.ps1` for easy startup
- **Activate conda environment**: `conda activate whatsapp_cloud_env`
- **Set LOCAL_ENV=True**: For local development without Google Cloud

## 🆘 Troubleshooting

### Import Errors
- Make sure you're running from the project root
- Use the launcher scripts (`run.bat` or `run.ps1`)
- Check that all `__init__.py` files exist

### Environment Issues
- Verify `.env` file exists and `LOCAL_ENV=True`
- Check conda environment is activated
- Ensure all dependencies are installed

### Port Issues
- Default port is 8001
- Change in `main.py` if needed
- Check if port is already in use 