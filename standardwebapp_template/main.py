import dataiku
from flask import Flask, render_template, jsonify

app = Flask(__name__)


# Route for the main page
@app.route("/")
def index():
    return render_template("index.html")


# Route to fetch data as JSON
@app.route("/data")
def get_data():
    dataset = dataiku.Dataset("seated_diners_2025_vs_2024")
    df = dataset.get_dataframe()
    # Convert dataframe to a dictionary for JSON response
    data = {
        "dates": df.columns[1:].tolist(),  # Assuming first column is region
        "regions": df.to_dict(orient="records"),
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run()
