# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister students from activities
- Persistent SQLite database storage
- Migration-based schema and seed data setup

## Getting Started

1. Install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. Apply database migrations and seed data:

   ```
   python run_migrations.py
   ```

3. Run the application:

   ```
   python app.py
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## Database

- Engine: SQLite (local development)
- Database file: `src/data/school.db`
- Migrations: SQL files in `src/migrations`

The schema is relational and Postgres-ready in structure:

- `activities`
- `students`
- `enrollments`
- `schema_migrations`

To reset local data, delete `src/data/school.db` and re-run migrations.

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                      |

## Data Model

The application uses a relational data model:

1. **Activities**
   - Name (unique)
   - Description
   - Schedule
   - Maximum number of participants allowed

2. **Students**
   - Email (unique)

3. **Enrollments**
   - Activity-to-student relationship
   - Enrolled timestamp

Data is persisted in SQLite and survives server restarts.
