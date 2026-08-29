# KanMind Backend

**KanMind** backend is a REST API built with Django and Django REST Framework, designed to work for a collaborative Kanban project management application. It manages secure user authentication, boards, tasks and comments.

This backend is built to serve the **KanMind Frontend Project**. You can find the corresponding vanilla JavaScript client application in the following repository:

👉 [KanMind Frontend Repository](https://github.com/Developer-Akademie-Backendkurs/project.KanMind)

## Features

- **User Authentication:** Registration and token-based authentication
- **Board Management:** Create and manage boards with owners and members
- **Task Management:** Create tasks with status, priority and due dates
- **Task Assignment:** Define an assignee and a reviewer for each task
- **Comment System:** Add and track comments directly on tasks
- **Access Control:** Secure, permission-based access to boards and tasks

## Project Structure

The codebase is organized into modular Django apps to isolate business logic:

- `core/` – Central system settings, configurations, and global routing
- `auth_app/` – Handlers for user registration, profile data and login
- `boards_app/` – Databases and endpoints managing individual boards
- `tasks_app/` – Data models for tasks, comments, priority flags and assignments

## Tech Stack

- **Framework:** Django & Django REST Framework
- **Language:** Python 3.x
- **Database:** SQLite (`db.sqlite3` - included by default)

## Installation & Local Setup

To get a local copy of the project up and running, follow these steps:

### 1. Clone the repository

```bash
git clone https://github.com/natgian/kanmind-backend.git
cd kanmind-backend
```

### 2. Set up a virtual environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install required dependencies

```bash
pip install -r requirements.txt
```

### 4. Execute database migrations

Apply the migrations to generate your local `db.sqlite3` file:

```bash
python manage.py migrate
```

### 5. Create an administrative user

Set up credentials for the central Django administration panel:

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

## API Endpoints

A reference map of the REST endpoints exposed by the server:

| Feature            | Endpoint                         | Method   | Description                                                                            |
| :----------------- | :------------------------------- | :------- | :------------------------------------------------------------------------------------- |
| **Authentication** | `/api/registration/`             | `POST`   | Register a new user                                                                    |
|                    | `/api/login/`                    | `POST`   | Validate credentials and return auth token                                             |
| **Boards**         | `/api/boards/`                   | `GET`    | Retrieve a list of boards that the logged-in user has either created or is a member of |
|                    | `/api/boards/`                   | `POST`   | Create a new board with the user as owner                                              |
|                    | `/api/boards/<id>`               | `GET`    | Retrieve information about a specific board                                            |
|                    | `/api/boards/<id>/`              | `PATCH`  | Update a board                                                                         |
|                    | `/api/boards/<id>/`              | `DELETE` | Delete a board                                                                         |
|                    | `/api/email-check/`              | `GET`    | Check if email is already registered to a user                                         |
| **Tasks**          | `/api/tasks/`                    | `POST`   | Creates a new task                                                                     |
|                    | `/api/tasks/assigned-to-me/`     | `GET`    | Retrieve all tasks assigned to the currently authenticated user                        |
|                    | `/api/tasks/reviewing/`          | `GET`    | Retrieve all tasks for which the currently authenticated user is the reviewer          |
|                    | `/api/tasks/<id>/`               | `PATCH`  | Update a task                                                                          |
|                    | `/api/tasks/<id>/`               | `DELETE` | Delete a task                                                                          |
|                    | `/api/tasks/<id>/comments/`      | `GET`    | Retrieve all comments associated with a specific task                                  |
|                    | `/api/tasks/<id>/comments/`      | `POST`   | Create a comment on a specific task                                                    |
|                    | `/api/tasks/<id>/comments/<id>/` | `DELETE` | Delete a comment on a specific task                                                    |

## License & Purpose

This project was developed exclusively for educational purposes. You are free to use, modify, and explore this codebase for personal learning and development.

## Contact

For questions or feedback, please contact:

- Email: <contact@natgian.dev>
- GitHub: [natgian](https://github.com/natgian)
