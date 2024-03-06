from flask import Flask
from data_processing import process_data

app = Flask(__name__)

@app.route("/")
def hello_world():
    df = process_data()
    return df.to_html()

if __name__ == "__main__":
    app.run()