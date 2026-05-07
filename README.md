# YTM-to-Navidrome: Automated Media Pipeline

A modular, multi-container automation suite that streamlines the process of capturing, tagging, and streaming music from YouTube Music into a private, self-hosted cloud.

This project demonstrates an end-to-end engineering workflow: from a frontend browser extension to a backend orchestration engine (n8n), down to specialized microservices (FastAPI/yt-dlp) and secure networking (Tailscale).

---

## 🚀 Architecture

| Stage | Component | Description |
|---|---|---|
| **Trigger** | Chrome Extension (MV3) | Captures Title, Artist, and URL from the YouTube Music player bar |
| **Orchestration** | n8n | Receives the webhook payload and handles download request logic |
| **Processing** | FastAPI + yt-dlp | Retrieves high-quality audio; FFmpeg handles ID3 tagging and cover-art injection |
| **Storage** | Docker Volume | Media is written to a shared volume, instantly picked up by Navidrome |
| **Access** | Tailscale MagicDNS | Exposes the full stack globally without opening public ports |

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| **Languages** | Python (FastAPI), JavaScript (Chrome Extension / n8n nodes) |
| **DevOps** | Docker, Docker Compose, Git (SSH-authenticated) |
| **Networking** | Tailscale (MagicDNS & Serve), ngrok (Webhook Ingress) |
| **Media Tools** | FFmpeg, yt-dlp, MusicBrainz API |
| **Automation** | n8n |

---

## 📁 Project Structure

```
.
├── downloader/            # Python FastAPI microservice (yt-dlp + FFmpeg)
│   ├── app.py             # Main API logic with BackgroundTasks
│   ├── Dockerfile         # Optimized slim Python image
│   └── requirements.txt   # Backend dependencies
├── extension/             # Chrome Extension source code
│   ├── manifest.json      # Manifest V3 configuration
│   └── background.js      # Metadata scraping & fetch logic
├── n8n/                   # Automation workflow
│   ├── workflow.json      # Exported n8n workflow
│   └── README.md          # Workflow documentation
└── docker-compose.yml     # Multi-container orchestration
```

---

## ⚙️ Setup & Installation

### 1. Backend Deployment

Ensure Docker and Tailscale are installed on your server, then clone and start the stack:

```bash
# Clone the repository via SSH
git clone git@github.com:piyush169/ytm-automation.git
cd ytm-automation

# Spin up all microservices
docker-compose up -d
```

### 2. Networking (Tailscale)

Enable **MagicDNS** in your Tailscale admin console to access the suite via a permanent hostname. On your Ubuntu server, accept DNS settings:

```bash
sudo tailscale up --accept-dns=true
```

### 3. Chrome Extension

1. Navigate to `chrome://extensions/`
2. Enable **Developer Mode**
3. Click **Load Unpacked** and select the `extension/` folder from this repo

---

## ✨ Key Technical Challenges Solved

**Session Persistence**
Resolved "Method Not Allowed" errors and session logout instability by migrating from temporary ngrok tunnels to a persistent Tailscale MagicDNS environment.

**Asynchronous Processing**
Implemented FastAPI `BackgroundTasks` to return an immediate webhook response to n8n, preventing timeouts during long-running yt-dlp download cycles.

**Automated Metadata**
Built a fuzzy-matching pipeline against the MusicBrainz API to correctly file tracks under their proper albums, even when YouTube Music metadata is incomplete or inconsistent.

**Secure Authentication**
Migrated from HTTPS PAT-based Git access to SSH key authentication for secure, credential-free automated deployments.
