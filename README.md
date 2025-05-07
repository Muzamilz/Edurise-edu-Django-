# Edurise - Modern Education Platform

Edurise is a comprehensive Django-based education platform that provides a modern and interactive learning experience for students, teachers, and administrators.

## Features

- **User Authentication & Authorization**
  - Separate dashboards for students, teachers, and administrators
  - Secure login and registration system
  - Role-based access control

- **Course Management**
  - Create and manage courses
  - Upload course materials
  - Track student progress
  - Interactive learning content

- **Class Management**
  - Schedule and manage classes
  - Real-time class updates
  - Attendance tracking
  - Class materials and resources

- **Program Management**
  - Create and manage educational programs
  - Program enrollment
  - Progress tracking
  - Certificate generation

- **Blog System**
  - Educational articles and updates
  - Interactive comments
  - Rich text content

- **Zoom Integration**
  - Seamless video conferencing
  - Class scheduling
  - Meeting management

## Technology Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Additional Tools**: Zoom API Integration

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/edurise.git
   cd edurise
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add necessary environment variables (see `.env.example`)

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
edurise/
├── admin_tools/         # Admin dashboard and tools
├── authentication/      # User authentication and authorization
├── blog/               # Blog system
├── classes/            # Class management
├── courses/            # Course management
├── enrollments/        # Student enrollment system
├── profiles/           # User profiles
├── programs/           # Program management
├── static/             # Static files (CSS, JS, images)
├── media/              # User-uploaded files
├── zoom_integration/   # Zoom API integration
└── manage.py           # Django management script
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Acknowledgments

- Django Framework
- Zoom API
- All contributors and users of the platform 