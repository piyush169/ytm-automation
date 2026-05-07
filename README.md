YTM-to-Navidrome: Automated Media Pipeline
A modular, multi-container automation suite that streamlines the process of capturing, tagging, and streaming music from YouTube Music into a private, self-hosted cloud.

This project demonstrates an end-to-end engineering workflow: from a frontend browser extension to a backend orchestration engine (n8n), down to specialized microservices (FastAPI/yt-dlp) and secure networking (Tailscale).

# 🚀 The Architecture
Trigger: A custom Chrome Extension (Manifest V3) captures metadata (Title, Artist, URL) directly from the YouTube Music player bar.

Orchestration: Data is dispatched via a secure webhook to an n8n instance. The workflow parses the payload and handles the logic-gate for the download request.

Processing: An asynchronous FastAPI microservice receives the metadata. It utilizes yt-dlp for high-quality audio retrieval and FFmpeg for automated ID3 tagging and cover-art injection.

Storage & Delivery: Media is stored in a shared Docker Volume, where it is instantly picked up by Navidrome.

Access: The entire stack is accessible globally and securely via Tailscale MagicDNS, providing a permanent, stable session without exposing public ports.

# 🛠️ Tech Stack
Languages : Python (FastAPI), JavaScript (Chrome Extension / n8n nodes).

DevOps: Docker, Docker Compose, Git (SSH-authenticated).

Networking: Tailscale (MagicDNS & Serve), ngrok (Webhook Ingress).

Media Tools: FFmpeg, yt-dlp, MusicBrainz API.

Automation: n8n.

# 📁 Project Structure

.
├── downloader/            # Python FastAPI API (yt-dlp + FFmpeg)
│   ├── app.py             # Main API logic with BackgroundTasks
│   ├── Dockerfile         # Optimized slim Python image
│   └── requirements.txt   # Backend dependencies
├── extension/             # Chrome Extension source code
│   ├── manifest.json      # Manifest V3 configuration
│   └── background.js      # metadata scraping & fetch logic
├── n8n/                   # Automation workflow
│   ├── workflow.json      # Exported n8n logic
│   └── README.md          # Workflow documentation
└── docker-compose.yml     # Multi-container orchestration

# ⚙️ Setup & Installation
1. Backend Deployment
Ensure you have Docker and Tailscale installed on your server.

Bash
# Clone the repository using SSH
`git clone git@github.com:piyush169/ytm-automation.git
cd ytm-automation`

# Spin up the microservices
`docker-compose up -d`
2. Networking (Tailscale)
Enable MagicDNS in your Tailscale console to access the suite via a permanent URL. On your Ubuntu server, ensure DNS settings are accepted:

Bash
`sudo tailscale up --accept-dns=true`
3. Extension Setup
Navigate to chrome://extensions/.

Enable Developer Mode.

Click Load Unpacked and select the extension/ folder from this repo.

# ✨ Key Technical Challenges Solved
Session Persistence: Solved "Method Not Allowed" and session logout issues by migrating from temporary ngrok tunnels to a stable Tailscale MagicDNS environment.

Asynchronous Processing: Implemented FastAPI BackgroundTasks to prevent n8n webhook timeouts during heavy yt-dlp download cycles.

Automated Metadata: Developed a fuzzy-matching logic using the MusicBrainz API to ensure tracks are filed under the correct albums even when YouTube metadata is incomplete.

Secure Authentication: Migrated from HTTPS PAT-based Git access to SSH Key authentication for automated, secure deployments.
