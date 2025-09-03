# Authentication-Django-App

Steps to Run the Project

1. Clone the repository
   git clone https://github.com/Rishith17/Authentication-Django-App.git

2. Navigate to the project directory
   cd Authentication-Django-App

3. Create a virtual environment
   virtualenv env

4. Activate the virtual environment
   - On Windows (PowerShell / CMD):
     .\env\Scripts\activate
   - On Linux / Mac:
     source env/bin/activate

5. Install dependencies
   pip install -r requirements.txt

6. Run migrations and start the server
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver


Project Requirements

- Python 3.8+
- Django (latest version as per requirements.txt)
- djangorestframework
- drf-yasg (for Swagger API docs)
- PyJWT or djangorestframework-simplejwt (for authentication if included)
- virtualenv (to create virtual environment)
- Postman (to test API endpoints)

(Exact versions are already listed in requirements.txt, so installing them will cover all.)


Testing with Postman

1. After running the server using:
   python manage.py runserver

2. Open Postman.

3. Use the base URL:
   http://127.0.0.1:8000/

4. Check your available endpoints (examples): 
   - (POST) To create a new user
   - (POST) To log in and get a token/session
   - (GET)  check user details (authorization required)
   - (Swagger Docs): http://127.0.0.1:8000/swagger/

5. If the endpoint requires authentication:
   - In Postman, we get the token and session id will be seen 
   - Paste the token you received after login

6. Verify responses:
   - 200 = Success
   - 400/401 = Error


Note

If you face any issue while configuring the repository,
feel free to contact me at: rishith.gs@gmail.com

