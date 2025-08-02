# Django REST API - User Management System

A robust Django REST API for user registration, authentication, and profile management with JWT authentication.

## 🚀 Features

- **Custom User Model**: Extends Django's AbstractBaseUser with email-based authentication
- **Profile Management**: Nested profile creation with role-based access
- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **Comprehensive Validation**: Email, phone number, and role validation
- **RESTful API**: Clean, well-documented REST endpoints
- **Database Transactions**: Ensures data consistency during user creation
- **Unit Tests**: Comprehensive test coverage for all functionality

## 🛠️ Technology Stack

- **Django 5.2.4**: Web framework
- **Django REST Framework 3.16.0**: API framework
- **djangorestframework-simplejwt 5.5.1**: JWT authentication
- **SQLite**: Database (default)
- **Python 3.10+**: Programming language

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (for version control)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd user_api
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 📚 API Endpoints

### Base URL
```
http://127.0.0.1:8000/
```

### 1. User Registration
**POST** `/register/`

Register a new user with profile information.

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "password_confirm": "password123",
    "profile": {
        "phone_number": "1234567890",
        "role": "student",
        "date_of_birth": "1990-01-01"
    }
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "is_active": true,
        "date_joined": "2024-01-01T00:00:00Z",
        "is_verified": false,
        "profile": {
            "phone_number": "1234567890",
            "role": "student",
            "date_of_birth": "1990-01-01"
        }
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 2. User Login
**POST** `/login/`

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "is_active": true,
        "date_joined": "2024-01-01T00:00:00Z",
        "is_verified": false,
        "profile": {
            "phone_number": "1234567890",
            "role": "student",
            "date_of_birth": "1990-01-01"
        }
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 3. Get Current User Profile
**GET** `/me/`

Get the current authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "is_active": true,
        "date_joined": "2024-01-01T00:00:00Z",
        "is_verified": false,
        "profile": {
            "phone_number": "1234567890",
            "role": "student",
            "date_of_birth": "1990-01-01"
        }
    }
}
```

## 🔐 Authentication

This API uses JWT (JSON Web Tokens) for authentication:

- **Access Token**: Valid for 60 minutes, used for API requests
- **Refresh Token**: Valid for 1 day, used to get new access tokens

### Using JWT Tokens

Include the access token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## ✅ Validation Rules

### User Registration
- **Email**: Must be unique and valid email format
- **Username**: Must be unique, 3+ characters, alphanumeric + underscores only
- **Password**: Minimum 8 characters, must match password_confirm
- **Password Confirm**: Required field for validation

### Profile Information
- **Phone Number**: Must be unique, 10+ digits, allows formatting characters
- **Role**: Must be one of: `student`, `vendor`, `admin`
- **Date of Birth**: Optional field

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts

# Run with verbose output
python manage.py test accounts --verbosity=2
```

## 📁 Project Structure

```
user_api/
├── accounts/                 # Main app directory
│   ├── migrations/          # Database migrations
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # User and Profile models
│   ├── serializers.py      # DRF serializers
│   ├── tests.py            # Unit tests
│   ├── urls.py             # URL routing
│   └── views.py            # API views
├── user_api/               # Project settings
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## 🔧 Configuration

### JWT Settings
JWT tokens are configured in `settings.py`:
- Access token lifetime: 60 minutes
- Refresh token lifetime: 1 day

### Database
Default configuration uses SQLite. For production, update `DATABASES` in `settings.py`.

## 🚨 Error Handling

The API provides detailed error messages for:
- Validation errors (400 Bad Request)
- Authentication failures (401 Unauthorized)
- Server errors (500 Internal Server Error)

### Common Error Responses

**Validation Error (400):**
```json
{
    "error": "Validation failed",
    "details": {
        "email": ["An account with this email already exists."],
        "password_confirm": ["You must confirm your password."]
    }
}
```

**Authentication Error (401):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team

## 🔄 Version History

- **v1.0.0**: Initial release with user registration, login, and profile management
- **v1.1.0**: Added comprehensive validation and error handling
- **v1.2.0**: Improved JWT authentication and added unit tests