from database import setup_database
from data_processing import process_data
from app import app

setup_database()
process_data()

if __name__ == "__main__":
    app.run()
