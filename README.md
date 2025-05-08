# Millo Airlines

A Django-based airline booking system that allows users to search, book, and manage flights.

## Features

- User authentication and registration
- Flight search and booking
- Seat selection
- User profile management
- Email verification
- Password reset functionality
- Admin dashboard
- Client dashboard

## Prerequisites

- Python 3.13.3 or higher
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Alejo-DB/millo_airlines.git
cd millo_airlines
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```
```bash
pip install reportlab
```
aplly this shi
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

5. Apply migrations:
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

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
millo_airlines/
├── accounts/           # User authentication and profile management
├── flights/           # Flight booking and management
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
├── manage.py          # Django management script
└── requirements.txt   # Project dependencies
```

## Dependencies

- Django 4.2.10
- django-crispy-forms 2.1
- crispy-bootstrap5 2023.10
- django-environ 0.11.2
- dj-database-url 2.1.0
- python-decouple 3.8
- django-allauth 0.58.2
- django-tables2 2.7.0
- django-filter 23.5
- django-widget-tweaks 1.5.0
- Pillow 11.2.1
- django-auditlog 2.3.0

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Alejandro Areiza Alzate - alejandro.workspace@outlook.com

Project Link: [https://github.com/yourusername/millo_airlines](https://github.com/yourusername/millo_airlines) 
