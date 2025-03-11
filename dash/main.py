# import dataiku
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime, timedelta

# Initialize Dash app
app = dash.Dash(__name__)

# Load dataset
# dataset = dataiku.Dataset("seated_diners_2025_vs_2024")
# df = dataset.get_dataframe()
df = pd.read_csv("data.csv")


# Helper functions
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
                week_values.append(float(region_row[date].replace("%", "")))
            else:
                weekly_data[region].append(
                    round(sum(week_values) / len(week_values), 1)
                )
                week_values = [float(region_row[date].replace("%", ""))]
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
            month_values = [
                float(region_row[date].replace("%", ""))
                for date in date_cols
                if datetime.strptime(f"2025-{date}", "%Y-%m/%d").month == month_num
            ]
            monthly_data[month][region] = (
                round(sum(month_values) / len(month_values), 1) if month_values else 0
            )
    return monthly_data


# Precompute data
weekly_data = aggregate_weekly(df)
week_labels = [f"Week {i+1}" for i in range(len(weekly_data["Global"]))]
monthly_data = aggregate_monthly(df)
month_labels = list(monthly_data.keys())

# Layout
app.layout = html.Div(
    [
        # Header
        html.Img(
            src="https://www.opentable.com/img/OpenTable-logo.svg",
            style={"width": "150px", "display": "block", "margin": "0 auto"},
        ),
        html.H1(
            "The restaurant industry, by the numbers",
            style={"textAlign": "center", "color": "#333"},
        ),
        html.P(
            "A snapshot of dining demand compared to 2024.",
            style={"textAlign": "center"},
        ),
        # Dropdown
        html.Div(
            [
                html.Label("View: "),
                dcc.Dropdown(
                    id="view-select",
                    options=[
                        {"label": "Daily", "value": "daily"},
                        {"label": "Monthly", "value": "monthly"},
                        {"label": "Weekly", "value": "weekly"},
                    ],
                    value="daily",
                    style={"width": "200px", "display": "inline-block"},
                ),
            ],
            style={"textAlign": "right", "marginBottom": "20px"},
        ),
        # Content
        html.Div(id="content"),
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "padding": "20px",
        "backgroundColor": "#f5f5f5",
    },
)


# Callback to update content based on dropdown
@app.callback(Output("content", "children"), Input("view-select", "value"))
def update_content(view):
    if view == "daily":
        return [
            html.H2("Change in seated diners by day, 2025 vs. 2024"),
            dash_table.DataTable(
                columns=[{"name": "MONTH/DAY", "id": "Region"}]
                + [{"name": col, "id": col} for col in df.columns[1:]],
                data=df.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "border": "1px solid #ddd",
                },
                style_header={"backgroundColor": "#f8f8f8", "fontWeight": "bold"},
            ),
        ]
    elif view == "monthly":
        monthly_df = pd.DataFrame(monthly_data, index=df["Region"]).reset_index()
        return [
            html.H2("Change in seated diners by month, 2025 vs. 2024"),
            dash_table.DataTable(
                columns=[{"name": "MONTH", "id": "Region"}]
                + [{"name": month, "id": month} for month in month_labels],
                data=monthly_df.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "border": "1px solid #ddd",
                },
                style_header={"backgroundColor": "#f8f8f8", "fontWeight": "bold"},
            ),
        ]
    elif view == "weekly":
        return [
            html.H2("Change in seated diners by week, 2025 vs. 2024"),
            dcc.Graph(
                figure={
                    "data": [
                        {
                            "x": week_labels,
                            "y": weekly_data[region],
                            "type": "line",
                            "name": region,
                        }
                        for region in weekly_data
                    ],
                    "layout": {
                        "yaxis": {"title": "% Change"},
                        "margin": {"l": 50, "r": 50, "t": 50, "b": 50},
                    },
                }
            ),
        ]


# Footer (optional, added outside callback for simplicity)
app.layout.children.append(
    html.Footer(
        [
            html.P("© 2025 OpenTable, Inc. All rights reserved."),
            html.P("Data provided by OpenTable. Cite and link back if used."),
        ],
        style={
            "textAlign": "center",
            "marginTop": "40px",
            "fontSize": "0.9em",
            "color": "#666",
        },
    )
)

if __name__ == "__main__":
    app.run_server(debug=True)
