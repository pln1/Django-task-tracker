# BjFlow

A task management platform built with Django. Designed to streamline team collaboration through intuitive drag-and-drop workflows and real-time updates.

## Tech Stack

* **Backend:** Python 3.12, Django 5
* **Database:** PostgreSQL
* **Frontend:** HTML5, CSS3, JavaScript, Fetch API (AJAX)
* **Infrastructure & Deployment:** Docker, Docker Compose

## Getting Started
**Build and start the containers:**
    ```bash
   docker compose up --build
    ```


**Apply database migrations:**
    ```bash
    docker compose exec web python manage.py migrate
    ```


**Create a superuser (admin account):**
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```


**Access the application:**
Open your browser and navigate to http://localhost:8000

### Prerequisites
* Docker and Docker Compose installed on your machine.

### Installation & Setup

**Clone the repository:**
   ```bash
   git clone [https://github.com/pln1/Django-task-tracker.git](https://github.com/pln1/Django-task-tracker.git)
   cd BjFlow
   ```

### Author
Oleksandr Polonskiy

Software Engineer | Student at KPI (FICE)

GitHub: @pln1

LinkedIn: Oleksandr Polonskiy