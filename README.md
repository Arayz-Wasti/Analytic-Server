# Analytics Server

A production-ready analytics backend built with FastAPI, designed for high-performance data ingestion, user management, analytics processing, and email notifications using an asynchronous architecture.

# Overview

Analytics Server is a scalable API service that:

Collects and processes analytics data

Manages users and authentication

Sends transactional email notifications

Stores and indexes data in MongoDB

Provides structured JSON logs for observability

Built with async-first design, suitable for microservices, dashboards, and event-driven systems.

✨ Key Features

⚡ High-performance FastAPI

🧵 Fully asynchronous architecture

📈 Analytics ingestion & indexing

👤 User management with JWT authentication

🔐 Secure token-based auth (access + refresh)

📧 Email service via SMTP (background tasks)

🗄️ MongoDB with async Motor driver

🧾 JSON structured logging

🧠 Middleware-based request tracking

🌐 Managed aiohttp client sessions

♻️ Graceful startup & shutdown lifecycle

🏗 Architecture
Client / Frontend
        ↓
   FastAPI Gateway
        ↓
 ┌──────────────────┐
 │  Analytics APIs  │
 │  User APIs       │
 │  Email Service   │
 └──────────────────┘
        ↓
    MongoDB

🛠 Tech Stack
Layer	Technology
Language	Python 3.10+
Framework	FastAPI
Database	MongoDB
DB Driver	Motor (Async)
Auth	JWT (PyJWT)
Email	SMTP
Logging	json-logging
Server	Uvicorn
HTTP Client	aiohttp
# Project Structure
# AnalyticServer/
│
├── backend/
│   ├── api/
│   │   ├── user/            # User & auth endpoints
│   │   ├── analytic/        # Analytics APIs
│   │   └── email_service/   # Email notifications
│   │
│   ├── utils/
│   │   ├── mongodb.py
│   │   ├── mongodb_indexes.py
│   │   └── aiohttp_client.py
│
├── main.py
├── requirements.txt
├── .env.example
└── README.md

# Installation
# Clone Repository
git clone https://github.com/Arayz-Wasti/Analytic-Server.git
cd Analytic-Server

# Virtual Environment
python -m venv .venv


Activate:

Windows

.venv\Scripts\activate


Linux / macOS

source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Environment Configuration

Create a .env file (never commit real secrets):

# Application
APP_NAME=AnalyticsServer

# Database
MONGO_URI=mongodb://localhost:27017
DB_NAME=analytic_server

# JWT Security
JWT_ALGORITHM=HS256
JWT_SECRET=your_secure_secret
JWT_ACCESS_EXPIRES=14400
JWT_REFRESH_EXPIRES=2592000

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=Analytics Server <your_email@gmail.com>

# External APIs
OPENWEATHER_API_KEY=your_api_key

# Running the Application
Development
uvicorn main:app --reload --port 8001

Production (Recommended)
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 4

# API Documentation
Tool	URL
Swagger UI	/docs
ReDoc	Disabled

Example:

http://localhost:8001/docs

# Application Lifecycle
Startup

Connects to MongoDB

Creates analytics indexes

Initializes HTTP client pool

Enables JSON logging

Shutdown

Gracefully closes DB connections

Closes HTTP client sessions

Flushes logs

🔐 Authentication & Security

JWT-based authentication

Secure password hashing (bcrypt)

Access & Refresh tokens

Environment-based secrets

No hardcoded credentials

📬 Email Service

Background email delivery

SMTP-based (Gmail supported)

Non-blocking async execution

Centralized configuration

🧾 Logging & Observability

JSON structured logs

Request body capture middleware

Suitable for:

ELK Stack

Grafana Loki

Cloud logging systems
