# 🌍 Tankas App

A FastAPI-based backend for the Cleanup Warriors application - a community-driven platform for reporting and resolving environmental cleanup issues with gamification features.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Key Features Explanation](#key-features-explanation)
- [Testing](#testing)
- [Deployment](#deployment)

## ✨ Features

- **User Authentication**: JWT-based authentication with signup and login
- **Issue Management**: Create, update, and resolve cleanup issues
- **GPS Location**: GeoJSON-based location storage for geospatial queries
- **Image Upload**: Automatic image compression and storage
- **Gamification**: Points system and leaderboard
- **Warriors Listing**: View all cleanup warriors with their stats
- **Comments**: Add comments to issues
- **Dashboard**: User statistics and recent activity
- **Public Events**: Public endpoint for viewing all cleanup events

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB (with Motor async driver)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib with Bcrypt
- **Image Processing**: Pillow
- **Validation**: Pydantic v2
- **ASGI Server**: Uvicorn

## 📁 Project Structure

```
cleanup-warriors-backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration settings
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── users.py          # User management endpoints
│   │   │   ├── warriors.py       # Warriors listing endpoints
│   │   │   ├── issues.py         # Issue management endpoints
│   │   │   ├── events.py         # Public events endpoints
│   │   │   └── rewards.py        # Rewards and leaderboard
│   │   └── dependencies.py        # Auth dependencies
│   │
│   ├── core/
│   │   ├── database.py           # MongoDB connection
│   │   └── security.py           # JWT and password hashing
│   │
│   ├── models/
│   │   ├── user.py               # User data model
│   │   ├── issue.py              # Issue data model
│   │   └── reward.py             # Reward data model
│   │
│   ├── schemas/
│   │   ├── auth.py               # Auth request/response schemas
│   │   ├── user.py               # User schemas
│   │   ├── issue.py              # Issue schemas
│   │   └── dashboard.py          # Dashboard schemas
│   │
│   ├── services/
│   │   ├── auth_service.py       # Authentication logic
│   │   ├── user_service.py       # User operations
│   │   ├── warrior_service.py    # Warriors listing logic
│   │   ├── issue_service.py      # Issue operations
│   │   ├── location_service.py   # GPS coordinate handling
│   │   └── storage_service.py    # File upload handling
│   │
│   └── utils/
│       ├── image_processing.py   # Image compression
│       └── point_calculator.py   # Points calculation
│
├── uploads/                       # User uploaded images
├── tests/                         # Test files
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.10+
- MongoDB 4.4+
- pip

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cleanup-warriors-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create uploads directory**
   ```bash
   mkdir -p uploads
   ```

## ⚙️ Configuration

1. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your settings**
   ```env
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=cleanup_warriors

   # Security (IMPORTANT: Change in production!)
   SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # File Upload
   UPLOAD_DIR=./uploads
   MAX_FILE_SIZE=5242880
   ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

   # AWS S3 (Optional)
   USE_S3=false
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   AWS_BUCKET_NAME=
   AWS_REGION=us-east-1

   # CORS
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

3. **Generate a secure secret key**
   ```bash
   openssl rand -hex 32
   ```

## 🏃 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker (Optional)

```bash
docker build -t cleanup-warriors-backend .
docker run -p 8000:8000 cleanup-warriors-backend
```

## 📖 API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

#### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token

#### Users
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `GET /api/users/dashboard` - Get user dashboard stats

#### Warriors
- `GET /api/warriors` - Get all cleanup warriors (sorted by points)
- `GET /api/warriors/{user_id}` - Get specific warrior details

#### Issues
- `GET /api/issues` - Get all issues (with filters)
- `POST /api/issues` - Create new issue (with image + GPS)
- `GET /api/issues/{id}` - Get issue details
- `PUT /api/issues/{id}` - Update issue
- `POST /api/issues/{id}/resolve` - Mark issue as resolved
- `POST /api/issues/{id}/comments` - Add comment to issue

#### Events (Public)
- `GET /api/events` - Get all events (no authentication required)

#### Rewards
- `GET /api/rewards` - Get all rewards
- `GET /api/rewards/leaderboard` - Get top users by points

## 🗄️ Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  hashed_password: String,
  display_name: String,
  avatar: String,
  points: Number,
  tasks_completed: Number,
  tasks_reported: Number,
  areas_cleaned: Number,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Issues Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: users),
  title: String,
  description: String,
  location: {
    type: "Point",
    coordinates: [longitude, latitude]  // GeoJSON
  },
  picture_url: String,
  priority: String ("low", "medium", "high"),
  difficulty: String ("easy", "medium", "hard"),
  status: String ("open", "in_progress", "resolved"),
  points_assigned: Number,
  reward_listing: String,
  comments: Array,
  resolved_by: ObjectId,
  resolved_at: DateTime,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Rewards Collection
```javascript
{
  _id: ObjectId,
  name: String,
  description: String,
  points_required: Number,
  image_url: String,
  available: Boolean,
  created_at: DateTime
}
```

### Indexes
- `users.username` (unique)
- `users.email` (unique)
- `issues.location` (2dsphere for geospatial queries)
- `issues.status`

## 🎯 Key Features Explanation

### GPS Location Handling

The application uses GeoJSON format for storing location data:

**Frontend sends:**
```json
{
  "latitude": 5.6037,
  "longitude": -0.1870
}
```

**Backend stores:**
```json
{
  "type": "Point",
  "coordinates": [-0.1870, 5.6037]  // [lng, lat]
}
```

This enables MongoDB geospatial queries for features like "find nearby issues".

### Image Upload Process

1. Accept multipart/form-data from frontend
2. Validate file type and size
3. Compress and resize image (max 1920x1080)
4. Generate unique filename (UUID)
5. Save to `uploads/YYYY/MM/` directory
6. Return URL to store in database

### Points System

Points are automatically calculated based on:
- **Difficulty**: Easy (10), Medium (20), Hard (30)
- **Priority**: Low (×1.0), Medium (×1.5), High (×2.0)

Example: A "hard" difficulty issue with "high" priority = 30 × 2.0 = 60 points

### Authentication Flow

1. User signs up → password is hashed and stored
2. User logs in → JWT token is generated and returned
3. Protected endpoints require `Authorization: Bearer <token>` header
4. Token is validated on each request

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## 🚢 Deployment

### Environment Setup

1. Set up MongoDB (MongoDB Atlas or self-hosted)
2. Configure environment variables
3. Set strong `SECRET_KEY`
4. Update `ALLOWED_ORIGINS` for your frontend domain

### Deployment Options

**Heroku**
```bash
heroku create cleanup-warriors-api
heroku config:set MONGODB_URI=<your-mongodb-uri>
git push heroku main
```

**AWS EC2**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone and setup
git clone <repo>
cd cleanup-warriors-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/cleanup-warriors.service
sudo systemctl start cleanup-warriors
sudo systemctl enable cleanup-warriors
```

**Docker**
```bash
docker build -t cleanup-warriors-backend .
docker run -d -p 8000:8000 --env-file .env cleanup-warriors-backend
```

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `MONGODB_URI` to production database
- [ ] Update `ALLOWED_ORIGINS` with production frontend URL
- [ ] Enable HTTPS
- [ ] Set up backup for MongoDB
- [ ] Configure logging and monitoring
- [ ] Set up rate limiting (optional)
- [ ] Use cloud storage for images (S3)

## 📝 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Known Issues

None at the moment. Please report any issues you encounter.

---

Built with ❤️ using FastAPI and MongoDB