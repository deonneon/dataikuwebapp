# import dataiku
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from flask import Flask

# Flask server for Dataiku
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__, server=server, url_base_pathname="/")

# Load data from Dataiku dataset
# dataset = dataiku.Dataset("seated_diners_2025_vs_2024")
# df = dataset.get_dataframe()

df = pd.read_csv("dash_template/data.csv")

# Prepare data for table and graph
dates = df.columns[1:]  # Exclude region column
regions = df.iloc[:, 0].tolist()  # First column as regions

# Weekly aggregation for graph (assuming daily data can be grouped by week)
weekly_df = df.copy()
weekly_df.columns = ["Region"] + [
    pd.to_datetime(d, format="%m/%d").strftime("%Y-%m-%d") for d in dates
]
weekly_df = weekly_df.melt(id_vars=["Region"], var_name="Date", value_name="Change")
weekly_df["Week"] = pd.to_datetime(weekly_df["Date"]).dt.strftime("%Y-W%U")
weekly_data = weekly_df.groupby(["Region", "Week"])["Change"].mean().reset_index()

# Layout
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.Img(
                    src="https://www.opentable.com/img/OpenTable-logo.svg",
                    style={"width": "150px"},
                ),
                html.H1("The restaurant industry, by the numbers"),
                html.P("A snapshot of dining demand compared to 2024."),
            ],
            style={"textAlign": "center", "padding": "20px"},
        ),
        # Main content
        html.Div(
            [
                html.H2("Change in seated diners by month / day, 2025 vs. 2024"),
                dash_table.DataTable(
                    id="table",
                    columns=[{"name": "MONTH/DAY", "id": df.columns[0]}]
                    + [{"name": d, "id": d} for d in dates],
                    data=df.to_dict("records"),
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "center",
                        "padding": "10px",
                        "border": "1px solid #ddd",
                    },
                    style_header={"backgroundColor": "#f8f8f8", "fontWeight": "bold"},
                    style_data={"backgroundColor": "#fff"},
                ),
                html.H2("Change in seated diners by week, 2025 vs. 2024"),
                dcc.Graph(
                    id="weekly-graph",
                    figure=px.line(
                        weekly_data,
                        x="Week",
                        y="Change",
                        color="Region",
                        title="Weekly Change in Seated Diners",
                        labels={"Change": "YoY Change (%)"},
                    ),
                ),
            ],
            style={"maxWidth": "1200px", "margin": "0 auto"},
        ),
        # Footer
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
        ),
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f5f5f5",
        "padding": "20px",
    },
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
