# import dataiku
from flask import Flask, render_template, jsonify, abort
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get the absolute path to the data file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.csv")


# Route for the main page
@app.route("/")
def index():
    return render_template("index.html")


# Route to fetch data as JSON
@app.route("/data")
def get_data():
    try:
        # Check if file exists
        if not os.path.exists(DATA_FILE):
            logger.error(f"Data file not found: {DATA_FILE}")
            abort(500, description="Data file not found")

        # Read the CSV file
        df = pd.read_csv(DATA_FILE)

        # Validate data structure
        if "Region" not in df.columns and len(df.columns) < 2:
            logger.error(
                "Invalid data format: missing Region column or insufficient data"
            )
            abort(500, description="Invalid data format")

        # Clean percentage values in the dataframe
        for col in df.columns[1:]:  # Skip the Region column
            # Clean the percentage values to ensure they contain numeric values
            df[col] = (
                df[col]
                .apply(
                    lambda x: (
                        str(x).replace("%", "")
                        if isinstance(x, (str, int, float))
                        else x
                    )
                )
                .astype(float)
            )

        # Convert dataframe to a dictionary for JSON response
        data = {
            "dates": df.columns[1:].tolist(),  # Assuming first column is region
            "regions": df.to_dict(orient="records"),
        }
        return jsonify(data)

    except Exception as e:
        logger.exception(f"Error processing data: {str(e)}")
        abort(500, description=f"Server error: {str(e)}")


# Error handler for 500 errors
@app.errorhandler(500)
def server_error(e):
    return jsonify(error=str(e)), 500


if __name__ == "__main__":
    logger.info(f"Starting server with data file: {DATA_FILE}")
    app.run(debug=True, host="0.0.0.0", port=5000)
