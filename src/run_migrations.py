from database import DB_PATH, run_migrations


if __name__ == "__main__":
    run_migrations()
    print(f"Migrations applied successfully. Database: {DB_PATH}")
