# Assistu Server

**Assistu** is an intelligent voice-enabled student assistant server built with Django and MongoDB. This is the backend API server that powers the Assistu application, providing RESTful endpoints for task management, note-taking, event scheduling, study planning, and more.

> **Client Repository**: Access the Client `web-application` of this server via [Assistu-Client](https://github.com/BazilSuhail/Assistu-Client)

---

## Overview

Assistu Server is a Django REST Framework-based backend that processes voice commands and provides academic management capabilities for students. It uses MongoDB for data storage, JWT for authentication, and integrates machine learning models for semantic search and intelligent text processing `all-MiniLM-L6-v2`.

---

## Key Features

### Authentication & User Management
- User registration and login with JWT authentication
- Secure password hashing and token-based authentication
- User profile management with customizable themes and avatars

### Task Management
- Create, update, delete, and view tasks via voice commands
- Task categorization by type (assignment, study, project, exam)
- Priority levels (low, medium, high) and status tracking
- Due date management and estimated duration tracking
- Tags and subject-based organization

### Event Scheduling
- Create and manage calendar events with voice input
- Event types: study sessions, classes, meetings, exams
- Link events to related tasks
- Time-based event management

### Intelligent Note-Taking
- Upload PDF documents or create text-based notes
- Automatic transcription and summarization
- Semantic note search using **all-MiniLM-L6-v2** embedding model
- Find similar notes based on content similarity
- Keyword extraction and categorization
- Importance levels and tagging system

### Study Planner
- Generate comprehensive study plans based on user input
- Subject-based planning with customizable duration
- Session breakdown and scheduling
- Plan management (create, view, delete)

### Notifications
- Task and event reminders
- Priority-based notification system
- Related entity tracking

---

## Technology Stack

- **Framework**: Django 4.x with Django REST Framework
- **Database**: MongoDB with MongoEngine ODM
- **Authentication**: JWT (djangorestframework-simplejwt)
- **ML/AI**: 
  - ONNX Runtime for model inference
  - Transformers library
  - all-MiniLM-L6-v2 for semantic search
- **PDF Processing**: PyMuPDF (fitz)
- **Server**: Uvicorn (ASGI server)
- **Environment Management**: python-dotenv

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running locally
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/BazilSuhail/Assistu-Server.git
cd Assistu-Server
```

### Step 2: Create Virtual Environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root with the following variables:
```env
SECRET_KEY=your-django-secret-key
GROQ_API_KEY=your-groq-api-key
GROQ_LLM_URL=https://api.groq.com/openai/v1/chat/completions
```

### Step 5: Start MongoDB
Ensure MongoDB is running on `mongodb://localhost:27017`

### Step 6: Run the Server
```bash
uvicorn assistu_project.asgi:application --reload
```

The server will start at `http://localhost:8000`

---

## Project Structure

```
assistu_project/
├── assistu_project/          # Main project configuration
│   ├── asgi.py              # ASGI configuration for Uvicorn
│   ├── settings.py          # Django settings (DB, CORS, JWT, etc.)
│   └── urls.py              # Main URL routing
│
├── users/                    # User authentication & management
│   ├── models.py            # User model with MongoEngine
│   ├── views.py             # Registration & login endpoints
│   ├── authentication.py    # JWT authentication logic
│   ├── backends.py          # MongoDB authentication backend
│   └── urls.py              # /api/auth/ routes
│
├── tasks/                    # Task management module
│   ├── models.py            # Task model (title, subject, priority, status, etc.)
│   ├── views.py             # CRUD operations for tasks
│   ├── utils.py             # LLM integration for task creation
│   └── urls.py              # /api/tasks/ routes
│
├── notes/                    # Note-taking & semantic search
│   ├── models.py            # Note model (transcript, summary, keywords)
│   ├── views.py             # Note CRUD and search endpoints
│   ├── utils.py             # PDF processing and summarization
│   ├── allMiniLm_utils.py   # Semantic search with all-MiniLM-L6-v2
│   └── urls.py              # /api/notes/ routes
│
├── events/                   # Calendar event management
│   ├── models.py            # Event model (title, type, start/end time)
│   ├── views.py             # Event CRUD operations
│   ├── utils.py             # Event processing logic
│   └── urls.py              # /api/events/ routes
│
├── planner/                  # Study plan generation
│   ├── models.py            # StudyPlan model (title, duration, sessions)
│   ├── views.py             # Plan creation and retrieval
│   ├── utils.py             # Plan generation logic
│   └── urls.py              # /api/planner/ routes
│
├── notifications/            # Notification system
│   ├── models.py            # Notification model (reminders, alerts)
│   ├── views.py             # Notification listing
│   └── urls.py              # /api/notifications/ routes
│
├── all-MiniLM-L6-v2/        # Pre-trained embedding model files
│
├── requirements.txt          # Python dependencies
├── manage.py                # Django management script
└── README.md                # Project documentation
```

---

## API Endpoints

### Authentication (`/api/auth/`)
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (returns JWT tokens)

### Tasks (`/api/tasks/`)
- `POST /api/tasks/create/` - Create task via LLM
- `GET /api/tasks/user/` - Get all user tasks
- `GET /api/tasks/<task_id>/` - Get specific task
- `PUT /api/tasks/update/` - Update task
- `DELETE /api/tasks/delete/` - Delete task

### Notes (`/api/notes/`)
- `GET /api/notes/all/` - Get all user notes
- `POST /api/notes/create/pdf/` - Create note from PDF
- `POST /api/notes/create/text/` - Create note from text
- `POST /api/notes/search-notes/` - Semantic search for similar notes
- `GET /api/notes/<note_id>/` - Get specific note
- `DELETE /api/notes/delete/<note_id>` - Delete note

### Events (`/api/events/`)
- `GET /api/events/` - List all events
- `POST /api/events/create/` - Create new event
- `GET /api/events/<event_id>/` - Get event details
- `PUT /api/events/update/<event_id>/` - Update event
- `DELETE /api/events/delete/<event_id>/` - Delete event

### Study Planner (`/api/planner/`)
- `GET /api/planner/` - List all study plans
- `POST /api/planner/` - Create new study plan
- `GET /api/planner/<plan_id>/` - Get plan details
- `DELETE /api/planner/delete/<plan_id>` - Delete plan

### Notifications (`/api/notifications/`)
- `GET /api/notifications/` - List user notifications

---

## Configuration

### CORS Settings
The server is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

Modify `CORS_ALLOWED_ORIGINS` in `settings.py` for production deployment.

### JWT Configuration
- Access token lifetime: 1 day
- Refresh token lifetime: 7 days
- Algorithm: HS256

### MongoDB Connection
Default connection: `mongodb://localhost:27017/assistu_db`

---

## Development

### Running in Development Mode
```bash
uvicorn assistu_project.asgi:application --reload
```

The `--reload` flag enables auto-restart on code changes.

### Database Collections
MongoDB collections used by the application:
- `users` - User accounts
- `tasks` - Task entries
- `notes` - Note documents
- `events` - Calendar events
- `study_plans` - Study planning data
- `notifications` - User notifications

---

## Contributing

This is the server component of the Assistu project. For the client-side application, visit the [Assistu-Client](https://github.com/BazilSuhail/Assistu-Client) repository.

---

## License

This project is part of an academic assistant application designed to help students manage their academic workflow through voice commands.

---

## Related Links

- **Client Repository**: [https://github.com/BazilSuhail/Assistu-Client](https://github.com/BazilSuhail/Assistu-Client)
- **Model**: all-MiniLM-L6-v2 for semantic similarity search [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

---

## Support

For issues, questions, or contributions, please open an issue in the GitHub repository.