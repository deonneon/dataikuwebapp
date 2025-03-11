# import dataiku
from flask import Flask, render_template, jsonify
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)


def aggregate_weekly(df):
    date_cols = [col for col in df.columns if col != "Region"]
    weekly_data = {}
    for region in df["Region"]:
        weekly_data[region] = []
        region_row = df[df["Region"] == region].iloc[0]
        week_start = datetime(2025, 1, 1)
        week_values = []
        for date in date_cols:
            current_date = datetime.strptime(f"2025-{date}", "%Y-%m/%d")
            if current_date < week_start + timedelta(days=7):
                # Clean the percentage value
                value = region_row[date]
                if isinstance(value, str):
                    value = value.replace("%", "")
                week_values.append(float(value))
            else:
                weekly_data[region].append(
                    round(sum(week_values) / len(week_values), 1)
                )
                # Clean the percentage value
                value = region_row[date]
                if isinstance(value, str):
                    value = value.replace("%", "")
                week_values = [float(value)]
                week_start += timedelta(days=7)
        if week_values:
            weekly_data[region].append(round(sum(week_values) / len(week_values), 1))
    return weekly_data


def aggregate_monthly(df):
    date_cols = [col for col in df.columns if col != "Region"]
    monthly_data = {"January": {}, "February": {}, "March": {}}
    for region in df["Region"]:
        region_row = df[df["Region"] == region].iloc[0]
        for month in monthly_data:
            month_num = {"January": 1, "February": 2, "March": 3}[month]
            month_values = []
            for date in date_cols:
                if datetime.strptime(f"2025-{date}", "%Y-%m/%d").month == month_num:
                    # Clean the percentage value
                    value = region_row[date]
                    if isinstance(value, str):
                        value = value.replace("%", "")
                    month_values.append(float(value))
            monthly_data[month][region] = (
                round(sum(month_values) / len(month_values), 1) if month_values else 0
            )
    return monthly_data


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    # dataset = dataiku.Dataset("seated_diners_2025_vs_2024")
    # df = dataset.get_dataframe()
    df = pd.read_csv("data.csv")

    # Daily data
    daily_data = {
        "dates": df.columns[1:].tolist(),
        "regions": df.to_dict(orient="records"),
    }

    # Weekly data
    weekly_data = aggregate_weekly(df)
    week_labels = [f"Week {i+1}" for i in range(len(weekly_data["Global"]))]

    # Monthly data
    monthly_data = aggregate_monthly(df)
    month_labels = list(monthly_data.keys())

    return jsonify(
        {
            "daily": daily_data,
            "weekly": {"labels": week_labels, "data": weekly_data},
            "monthly": {"labels": month_labels, "data": monthly_data},
        }
    )


if __name__ == "__main__":
    app.run()
