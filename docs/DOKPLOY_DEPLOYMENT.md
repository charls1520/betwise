# Dokploy Deployment Guide for Betwise

This document provides step-by-step instructions on how to deploy Betwise to your VPS using Dokploy.

## Prerequisites
- A VPS running Dokploy.
- Your project hosted on GitHub.

## Steps to Deploy

1.  **Log in** to your Dokploy dashboard.
2.  Navigate to the **Projects** section and create a new project (e.g., `betwise-project`).
3.  Inside the project, click **Create Application**.
4.  Select **Compose** as the application type.
5.  **Configure the Application:**
    -   **Name:** Give it a name like `betwise-compose`.
    -   **Source:** Choose **GitHub**. Select your repository `charls1520/betwise`.
    -   **Branch:** Select the branch `betwise-estable`.
    -   **Compose Path:** Enter `./docker-compose.prod.yml`
6.  **Set Environment Variables:**
    Go to the **Environment** tab of your Compose application and paste all the variables from your `.env` file. 
    
    **Crucial Configuration:**
    Since you are not using a domain, set the `VITE_API_URL` to the public IP of your VPS and the backend port we defined (`34568`).
    
    ```env
    # Example Environment Variables
    POSTGRES_USER=betwise_user
    POSTGRES_PASSWORD=your_secure_password
    POSTGRES_DB=betwise_db
    
    OLLAMA_BASE_URL=http://your_ollama_url
    LLM_MODEL_NAME=llama3
    OPENROUTER_API_KEY=your_key
    EMBEDDING_MODEL_NAME=nomic-embed-text
    ODDS_API_KEY=your_key
    TELEGRAM_BOT_TOKEN=your_bot_token
    TELEGRAM_CHAT_ID=your_chat_id
    
    # IMPORTANT: Point this to your VPS Public IP and backend port 34568
    VITE_API_URL=http://<YOUR_VPS_PUBLIC_IP>:34568
    ```
7.  Click **Deploy** or **Save and Deploy**.
8.  Dokploy will build the Docker images and start the containers. Check the **Deployments** or **Logs** tab to see the progress.

## Accessing the Application

Once deployed successfully, you can access your application at:
- **Frontend:** `http://<YOUR_VPS_PUBLIC_IP>:34567`
- **Backend API:** `http://<YOUR_VPS_PUBLIC_IP>:34568`