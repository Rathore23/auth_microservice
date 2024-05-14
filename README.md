# Auth Microservice

This project is a standalone application that provides secure user authentication
functionality, including OTP-based authentication, password reset, and account update.


## Note :

- I started working on 13/05/2024 at night and continued the next day, spending approximately 8 to 9 hours.
- I have provided an example .env file for configuring email and OTP settings.
- Twilio is used for OTP sending. If Twilio credentials are not available, OTPs will be sent in the response for testing purposes.


## Installation

1. Clone the repository:

```
git clone <repository_url>
```

2. Create a `.env` file and set environment variables:

```
python3 -m venv virtualenv
```

- For Window system

```
./virtualenv/Scripts/activate
```

- For Ubuntu System
```
source env/bin/activate
```

3. For install requirements.txt Packages

```
pip install -r requirements.txt
```

4. Configure database settings.

5. Running the Project

```
python manage.py migrate
python manage.py runserver
```

6. Create Superuser to access admin panel

```
python manage.py createsuperuser
```

Access the project at: http://127.0.0.1:8000/admin/
