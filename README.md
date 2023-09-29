<!-- Here I created the backend Assignment named project to handle below functionlities -->

- User registartion
- User login
- User post creation (ANy type of media audio, video, compressed images) (Given support for AWS. Please use your AWS secret credentials at below locations to use the functionalities successfully. )
 1. BackendAssignment\settings.py
 2. posts\utils.py 
- Update your database credentials in below location
 1. BackendAssignment\settings.py
- like and comments on the posts by user
- post categories based on various
- complete API with dynamic responses based on api endpoint

<!-- How to run project -->
- create vitual env

    pythom3 -m venv venv

- Activate the env
- install the requirements

    pip3 -r requirements.txt

- create migration on database

    python manage.py makemigrations
    python manage.py migrate

- run the server

    python manage.py runserver

<!-- please add the necessary secret value for AWS, Region and other related to run the project successfully -->