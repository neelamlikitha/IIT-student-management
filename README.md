# IIT Student Management System

A responsive Flask web application for managing student and teacher records and tracking student attendance. The original command-line example, `new student management.py`, is preserved; the web app is started separately with `app.py`.

## Features

- Dashboard with student, teacher, and attendance totals and recent attendance.
- Add, view, update, and delete student and teacher records.
- Record, view, update, and delete attendance by student and date.
- JSON file storage; attendance is stored with its student record.
- Server-side validation, browser form validation, confirmation prompts, and success/error messages.
- Responsive layouts for desktop and mobile screens.

## Project structure

```text
app.py                          Flask application and JSON storage
new student management.py       Original command-line example (unchanged)
templates/                      Jinja templates for the dashboard and management pages
static/css/style.css            Responsive application styles
static/js/app.js                Delete confirmation behavior
instance/records.json           Local data file (created when a record is saved)
requirements.txt                Python dependencies
render.yaml                     Render web service and persistent disk configuration
README.md                       Project and run instructions
```

## Run locally

Use Python 3.10 or later:

```bash
python -m venv .venv
```

Activate the environment, then install and run:

```bash
pip install -r requirements.txt
python app.py
```

Open [http://localhost:5000](http://localhost:5000). By default, records are written to `instance/records.json`. Set `DATA_FILE` to use another JSON file and `SECRET_KEY` to configure the Flask session key.

## Deploy to Render

Create a new Render Blueprint from this repository and use `render.yaml`. The service installs `requirements.txt`, runs with Gunicorn, and stores records at `/var/data/records.json` on a persistent disk. The configured Starter service and persistent disk incur Render charges; choose an appropriate plan before deploying.

## Data notes

The original Python file contains example records in its `main()` function, but does not load or save JSON data. No JSON data file was present in the project, so the web app starts with an empty record set and does not change or import those examples. The JSON file is created when the first record is saved.

