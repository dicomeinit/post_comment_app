# Project Setup Instructions

This project leverages Google Cloud's Vertex AI for AI-driven functionalities. Follow the instructions below to set
up the project and enable Vertex AI in Google Cloud Platform (GCP).

## Prerequisites
- Python 3.10+
- [Google Cloud Account](https://cloud.google.com/)

---

## 1. Clone the Repository and Install Dependencies

```bash
git clone https://github.com/dicomeinit/posts_comments.git
cd posts_comments_app
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```


## 2. Create and Configure the .env File

```bash
cp .env.example .env
```

Then, update the .env file with your project-specific values, such as PROJECT_ID for Google Cloud.

## 3. Setting Up Google Cloud Vertex AI
To use Vertex AI, you’ll need a GCP project with the Vertex AI API enabled.
Create a Google Cloud Project and enable the Vertex AI API.
Log in with the Google Cloud SDK on your local machine:

```bash
gcloud auth application-default login
```

## 4. Running the Project Locally
```bash
python manage.py migrate
python manage.py runserver
```

## 5. Running Tests and Checking Coverage

To run tests and view test coverage:

```bash
coverage run --source='.' manage.py test --noinput --keepdb && coverage report

```


## 6. Linting and Formatting with Ruff

Use Ruff to check and automatically fix linting and formatting issues.
To run Ruff checks and automatically fix issues:

```bash
ruff check --select I --fix
ruff format .

```

## 7. API Documentation and Testing

```plantuml
http://localhost:8000/api/docs/
```