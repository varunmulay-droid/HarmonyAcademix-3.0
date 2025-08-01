# Harmony Hands - Render Deployment Guide

## Prerequisites
1. GitHub account
2. Render account (render.com)
3. PostgreSQL database

## Deployment Steps

### 1. Prepare Your Repository
```bash
# Push your code to GitHub with these files:
# - render_requirements.txt
# - Procfile
# - runtime.txt
# - render.yaml (optional, for automatic setup)
# - main.py (your Flask app entry point)
```

### 2. Deploy on Render

#### Option A: Using render.yaml (Automatic)
1. Connect your GitHub repository to Render
2. Render will automatically detect the render.yaml file
3. It will create both the web service and PostgreSQL database

#### Option B: Manual Setup
1. **Create PostgreSQL Database:**
   - Go to Render Dashboard
   - Click "New +" → "PostgreSQL"
   - Name: `harmony-hands-db`
   - Choose your plan (Free tier available)
   - Note the connection details

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name:** `harmony-hands-erp`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r render_requirements.txt`
     - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT main:app`

### 3. Environment Variables
Set these in your Render web service settings:

```
DATABASE_URL=<your-postgres-connection-string>
SESSION_SECRET=<generate-a-random-secret-key>
FLASK_ENV=production
FLASK_DEBUG=0
```

### 4. File Structure for Deployment
```
harmony-hands/
├── main.py                 # Flask app entry point
├── app.py                  # App configuration
├── models.py               # Database models
├── routes.py               # Application routes
├── forms.py                # WTForms definitions
├── render_requirements.txt # Python dependencies
├── Procfile               # Process configuration
├── runtime.txt            # Python version
├── render.yaml            # Render configuration (optional)
├── static/                # CSS, JS, images
├── templates/             # Jinja2 templates
└── uploads/               # File uploads (create on server)
```

### 5. Database Migration
After deployment, the database tables will be created automatically when the app starts.

### 6. Important Notes
- Make sure your `main.py` imports the app correctly
- Ensure all file paths are relative, not absolute
- The `uploads` directory will be created automatically
- PostgreSQL connection will be handled via DATABASE_URL

### 7. Testing Deployment
1. Visit your Render app URL
2. Test user registration and login
3. Test form submissions
4. Verify file uploads work
5. Test PDF generation functionality

### 8. Troubleshooting
- Check Render logs for any errors
- Ensure all environment variables are set
- Verify PostgreSQL connection string
- Check file permissions and directory structure

## Security Considerations
- Never commit real environment variables to version control
- Use strong SESSION_SECRET in production
- Regularly update dependencies
- Monitor your application logs

## Support
- Render Documentation: https://render.com/docs
- PostgreSQL on Render: https://render.com/docs/databases