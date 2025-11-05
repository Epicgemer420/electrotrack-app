# ElectroTrack Deployment Guide

This guide covers multiple options for deploying your ElectroTrack app so friends can access it.

## Option 1: Streamlit Cloud (Easiest - Recommended for Quick Sharing) ⭐

**Free tier available!**

### Steps:

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create `requirements.txt` for Streamlit Cloud:**
   Make sure `requirements.txt` includes:
   ```
   streamlit>=1.28.0
   requests>=2.31.0
   ```

3. **Go to [Streamlit Cloud](https://streamlit.cloud/)**
   - Sign up/login with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

4. **Deploy Backend API separately:**
   - Option A: Use [Railway](https://railway.app/) or [Render](https://render.com/) for the FastAPI backend (see Option 2)
   - Option B: Include both frontend and backend in Streamlit (modify app.py to not require external API)

### Update app.py to use deployed API:
Set environment variable in Streamlit Cloud:
- Go to app settings
- Add secret: `ELECTROTRACK_API_URL` = `https://your-api-url.com`

---

## Option 2: Railway.app (Full Stack Deployment) 🚂

**Free tier with $5 credit/month**

### Steps:

1. **Sign up at [Railway.app](https://railway.app/)**

2. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

3. **Deploy Backend API:**
   ```bash
   cd /path/to/your/project
   railway init
   railway up
   ```
   Railway will detect your `server.py` and deploy it.

4. **Deploy Frontend (Streamlit):**
   - Create new service in Railway
   - Add `streamlit` to requirements.txt
   - Set start command: `streamlit run app.py --server.port $PORT`
   - Set environment variable: `ELECTROTRACK_API_URL=https://your-backend.railway.app`

5. **Get your URLs:**
   Railway provides public URLs for both services.

---

## Option 3: Render.com (Full Stack) 🎨

**Free tier available**

### Steps:

1. **Sign up at [Render.com](https://render.com/)**

2. **Deploy Backend API:**
   - New → Web Service
   - Connect GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3

3. **Deploy Frontend:**
   - New → Web Service
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Add environment variable: `ELECTROTRACK_API_URL=https://your-backend.onrender.com`

---

## Option 4: ngrok (Quick Testing - Not for Production) ⚡

**Free for testing with friends**

### Steps:

1. **Install ngrok:**
   ```bash
   # macOS
   brew install ngrok
   
   # Or download from https://ngrok.com/
   ```

2. **Start your backend:**
   ```bash
   python server.py
   ```

3. **Start your Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Create ngrok tunnels:**
   ```bash
   # Terminal 1: Backend tunnel
   ngrok http 8000
   
   # Terminal 2: Frontend tunnel
   ngrok http 8501
   ```

5. **Update app.py temporarily:**
   ```python
   API_BASE_URL = "https://your-ngrok-backend-url.ngrok.io"
   ```

**Note:** ngrok URLs change each time you restart. Great for testing, not for permanent sharing.

---

## Option 5: Self-Hosted with Domain (Advanced) 🌐

### Steps:

1. **Rent a VPS** (DigitalOcean, Linode, AWS EC2)

2. **Set up the server:**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip nginx
   
   # Install app dependencies
   pip3 install -r requirements.txt
   ```

3. **Use systemd to run services:**
   
   Create `/etc/systemd/system/electrotrack-api.service`:
   ```ini
   [Unit]
   Description=ElectroTrack API
   After=network.target
   
   [Service]
   User=your-user
   WorkingDirectory=/path/to/your/app
   ExecStart=/usr/bin/python3 server.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Create `/etc/systemd/system/electrotrack-app.service`:
   ```ini
   [Unit]
   Description=ElectroTrack Streamlit App
   After=network.target
   
   [Service]
   User=your-user
   WorkingDirectory=/path/to/your/app
   ExecStart=/usr/bin/streamlit run app.py --server.port 8501
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Configure Nginx:**
   ```nginx
   # /etc/nginx/sites-available/electrotrack
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /api/ {
           proxy_pass http://localhost:8000/;
       }
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

5. **Enable services:**
   ```bash
   sudo systemctl enable electrotrack-api
   sudo systemctl enable electrotrack-app
   sudo systemctl start electrotrack-api
   sudo systemctl start electrotrack-app
   sudo systemctl reload nginx
   ```

---

## Recommended Quick Setup for Friends

**Best option: Streamlit Cloud + Render/Railway**

1. **Deploy API to Render/Railway** (15 minutes)
2. **Deploy Streamlit app to Streamlit Cloud** (5 minutes)
3. **Share the Streamlit Cloud URL** ✨

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `ELECTROTRACK_API_URL` | Backend API URL | `https://api.example.com` |
| `PORT` | Server port (usually set by platform) | `8000` |

---

## Testing Your Deployment

1. **Check backend health:**
   ```bash
   curl https://your-api-url.com/health
   ```

2. **Test Streamlit app:**
   - Visit your Streamlit Cloud/Render URL
   - Try registering an athlete
   - Get a recommendation

---

## Troubleshooting

**API connection errors:**
- Check CORS settings in `server.py` (add FastAPI CORS middleware if needed)
- Verify `ELECTROTRACK_API_URL` environment variable
- Check if backend is running and accessible

**Import errors:**
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility (3.8+)

**Port binding errors:**
- Use `$PORT` environment variable provided by hosting platform
- Update start commands to use platform's port

---

## Security Notes

- Don't commit API keys or secrets to GitHub
- Use environment variables for sensitive data
- Consider adding authentication for production use
- Enable HTTPS (most platforms do this automatically)
