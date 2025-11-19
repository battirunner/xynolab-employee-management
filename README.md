# Employee Management API

A FastAPI-based employee management system with role-based authentication, attendance tracking, salary management, and email notifications.

## Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (Admin/Employee)
  - Secure password hashing

- **Employee Management**
  - Employee registration and profile management
  - Admin can create and manage employee accounts
  - Employee data includes personal info, department, position, salary

- **Attendance System**
  - Daily check-in/check-out functionality
  - Leave and holiday submissions
  - Attendance history tracking
  - Admin can view all employee attendance

- **Salary Management**
  - Monthly salary records
  - Overtime, bonus, and deduction tracking
  - Admin can update salary status (pending/paid)
  - Automated email notifications for salary updates

- **Email Notifications**
  - SMTP-based email system
  - Salary update notifications with CSV reports
  - Welcome emails for new employees
  - Customizable email templates

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database
- uv package manager

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd employee-management-api
```

2. Complete setup (installs dependencies, runs migrations, creates admin user):
```bash
make setup
```

3. Start the application:
```bash
make run
```

The API will be available at `http://localhost:8000`

### Manual Installation

If you prefer manual setup:

1. Install dependencies:
```bash
make install
# or: uv sync
```

2. Set up the database:
   - Create a PostgreSQL database named `employee-test`
   - Update the `.env` file with your database credentials

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run database migrations:
```bash
make migrate
# or: uv run alembic upgrade head
```

5. Create admin user:
```bash
make create-admin
# or: uv run python create_admin.py
```

6. Start the application:
```bash
make run
# or: uv run python run.py
```

## Available Make Commands

Run `make help` to see all available commands:

### Setup Commands
- `make install` - Install dependencies with uv
- `make migrate` - Run database migrations  
- `make create-admin` - Create initial admin user
- `make setup` - Full setup (install + migrate + create-admin)

### Run Commands
- `make run` - Start the production server
- `make dev` - Start the development server with auto-reload

### Database Commands
- `make migration` - Create a new migration
- `make db-upgrade` - Apply pending migrations
- `make db-downgrade` - Rollback last migration

### Development Commands
- `make test` - Run tests (when implemented)
- `make lint` - Run code linting
- `make format` - Format code
- `make clean` - Clean cache and temporary files

### Utility Commands
- `make check` - Check if app imports correctly
- `make logs` - Show application logs

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Schema

The application includes the following main entities:

- **Users**: Authentication and basic user information
- **Employees**: Employee-specific data (profile, salary, department)
- **Attendance**: Daily attendance records with check-in/out times
- **Salary Records**: Monthly salary information with status tracking

## Email Configuration

To enable email notifications, configure the SMTP settings in your `.env` file:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Employee Management System
```

## Usage

### Admin Functions
- Create user accounts
- Manage employee data
- View all attendance records
- Update salary records
- Generate salary reports

### Employee Functions
- Check-in/check-out
- View personal attendance history
- View salary records
- Submit leave requests

## Database Migrations

To create a new migration:
```bash
uv run alembic revision --autogenerate -m "Migration description"
```

To apply migrations:
```bash
uv run alembic upgrade head
```

## Development

For development, the application includes:
- Automatic reload with uvicorn
- SQLAlchemy ORM with Alembic migrations
- Pydantic models for request/response validation
- Comprehensive error handling
- Security best practices