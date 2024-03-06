from database import setup_database
from data_processing import process_data
from app import app
from database import mycursor, mydb

setup_database()

df = process_data()

if __name__ == "__main__":
    app.run()

mydb.close()