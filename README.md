# 📋 Runbook: Deploy & Test Your Flask App

---

## 🔧 Prerequisites

-  **Docker** & **Docker Compose** installed  
-  **Vagrant** installed and configured  
-  SSH key pair available (`~/.ssh/id_ed25519` + `.pub`)  
-  [Optional] **docker-slim** for image slimming  

---

## 🚀 1. First-Time Setup

1. **Install docker-slim** (if not already installed but want use it):
   ```bash
   brew install docker-slim
   ```
2. **Build the base image**
    ```bash
   docker build -t flask_app:latest .
   ```
3. **Create a slim image**
    ```bash
    docker-slim build \
    --tag flask_app:slim \
    --include-path /app/templates \
    --include-path /app/static \
    flask_app:latest
    ```
4. **Launch containers** (with fresh build)
    ```bash
   docker compose up --build -d
   ```

## 🔄 2. Subsequent Deployments

When your images are already built and you just want to spin up containers:

    ```bash
    docker compose up --build -d
   ```
   ```

## 💻 3. Configure heartbeat.sh

Open `heartbeat.sh` in your editor.

Replace the *.*.*.* with your host’s IP

## 💻 4. Bring Up & Provision Vagrant VMs in first usage

    ```bash
    vagrant up
    vagrant provision
    vagrant provision sftp1 sftp2 sftp3 --provision-with install_keys
    vagrant provision sftp1 sftp2 sftp3 --provision-with heartbeat_cron
   ```

## 🎉 You're all set! 🚀

    ```bash
    http://localhost:4000
    ```




   

