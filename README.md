# Social Media App

A simple social media application built with Django, HTML, and Bootstrap that allows users to create, read, update, and delete posts, as well as like and comment on posts.

## Features

- User authentication (register, login, logout)
- User profiles with profile pictures
- Create, read, update, and delete posts
- Like and unlike posts
- Comment on posts
- View posts by specific users
- Responsive design with Bootstrap

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd social_media_app
```

2. Create a virtual environment and activate it:
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Apply migrations:
```
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (admin):
```
python manage.py createsuperuser
```

6. Run the development server:
```
python manage.py runserver
```

7. Open your browser and navigate to `http://127.0.0.1:8000/`

## Usage

1. Register a new account or login with an existing account
2. Create a new post by clicking on "New Post" in the navigation bar
3. View all posts on the home page
4. Click on a post title to view the full post and its comments
5. Like posts by clicking the heart icon
6. Comment on posts by using the comment form on the post detail page
7. Update your profile by clicking on "Profile" in the navigation bar
8. View posts by a specific user by clicking on their username

## Technologies Used

- Django 5.2.1
- Bootstrap 5
- HTML/CSS
- JavaScript/jQuery
- SQLite (database)
- Crispy Forms (for form styling)
- Pillow (for image processing)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
