import psycopg2
import os


def setup_database():
    """
    Sets up the PostgreSQL database and creates the necessary tables.
    The database credentials are read from environment variables to keep them secure.
    """
    print("Setting up database...")

    # Use environment variables for secure database credentials
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    try:
        # Connect to the default database to create a new one if it doesn't exist
        conn_str = f"dbname=postgres user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the project database exists, create it if not
        try:
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {DB_NAME}")
                print(f"Database '{DB_NAME}' created.")
        except Exception as e:
            print(f"Error creating database: {e}")

        cursor.close()
        conn.close()

        # Connect to the newly created database
        conn_str = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        cursor = conn.cursor()

        # Create a table for users
        user_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(255) PRIMARY KEY,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(user_table_query)
        print("User table created or already exists.")

        # Create a table to store saved resume screening sessions
        sessions_table_query = """
        CREATE TABLE IF NOT EXISTS screening_sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            job_description TEXT NOT NULL,
            ranked_resumes JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );
        """
        cursor.execute(sessions_table_query)
        print("Screening sessions table created or already exists.")

        cursor.close()
        conn.close()
        print("Database setup complete.")

    except psycopg2.OperationalError as e:
        print(
            f"OperationalError: Could not connect to the database. Please check your PostgreSQL server and credentials. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    setup_database()
