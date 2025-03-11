# import dataiku
from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)


# Route for the main page
@app.route("/")
def index():
    return render_template("index.html")


# Route to fetch data as JSON
@app.route("/data")
def get_data():
    # dataset = dataiku.Dataset("seated_diners_2025_vs_2024")
    # df = dataset.get_dataframe()
    df = pd.read_csv("data.csv")

    # Clean percentage values in the dataframe
    for col in df.columns[1:]:  # Skip the Region column
        # Clean the "Change" column to ensure it contains numeric values
        df[col] = (
            df[col]
            .apply(lambda x: x.replace("%", "") if isinstance(x, str) else x)
            .astype(float)
        )

    # Convert dataframe to a dictionary for JSON response
    data = {
        "dates": df.columns[1:].tolist(),  # Assuming first column is region
        "regions": df.to_dict(orient="records"),
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run()
