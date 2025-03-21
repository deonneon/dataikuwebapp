# import dataiku
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from flask import Flask
from datetime import datetime

# Flask server for Dataiku
server = Flask(__name__)

# Dash app with custom styles
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname="/",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# Custom CSS for ExampleDash-like styling
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>State of the Restaurant Industry</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #fff;
                color: #333;
                line-height: 1.5;
            }
            .header {
                text-align: left;
                padding: 40px 20px;
            }
            .header h1 {
                font-size: 2.5em;
                color: #333;
                margin-bottom: 10px;
                font-weight: 600;
            }
            .header p {
                font-size: 0.9em;
                color: #555;
                max-width: 800px;
                margin: 0 auto;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }
            .dropdown-container {
                margin: 30px 0;
                text-align: left;
            }
            .chart-container {
                background-color: #fffdf5;
                border-radius: 8px;
                padding: 30px;
                margin-top: 20px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            .legend {
                display: flex;
                align-items: center;
                justify-content: flex-end;
                margin-bottom: 15px;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin-left: 20px;
            }
            .legend-color {
                width: 30px;
                height: 4px;
                margin-right: 8px;
            }
            .legend-label {
                font-size: 0.9em;
                color: #555;
            }
            .footer {
                text-align: center;
                margin-top: 60px;
                padding: 30px 0;
                font-size: 0.9em;
                color: #777;
            }
        </style>
        {%scripts%}
    </head>
    <body>
        {%app_entry%}
        <footer class="footer">
            <div class="container">
                <p>© 2025 ExampleDash, Inc. All rights reserved.</p>
                <p>Data provided by ExampleDash. Cite and link back if used.</p>
            </div>
        </footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
"""

# Load data from CSV with the first row as header
df = pd.read_csv("data.csv", header=0)  # Ensure the first row is treated as the header

# Prepare data for table and graph
dates = df.columns[1:]  # Exclude region column
regions = df.iloc[:, 0].tolist()  # First column as regions

# Add the current year to the date columns for proper parsing
current_year = datetime.now().year
df.columns = ["Region"] + [f"{d}/{current_year}" for d in dates]

# Convert to long format for plotting
plot_df = df.copy()
plot_df = plot_df.melt(id_vars=["Region"], var_name="Date", value_name="Change")

# Clean the "Change" column to ensure it contains numeric values
plot_df["Change"] = plot_df["Change"].str.replace("%", "", regex=False).astype(float)

# Convert dates to datetime objects for proper sorting
plot_df["Date"] = pd.to_datetime(plot_df["Date"], format="%m/%d/%Y")

# Sort by date to ensure chronological order
plot_df = plot_df.sort_values("Date")


# Function to create the figure with ExampleDash styling
def create_figure(data):
    # Filter to just show Global data initially
    filtered_data = data[data["Region"] == "Global"]

    # Create a custom figure instead of using px
    figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Change"],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Global",
                "line": {
                    "color": [
                        "#2ecc71" if val >= 0 else "#e74c3c"
                        for val in filtered_data["Change"]
                    ],
                    "width": 2,
                    "shape": "spline",
                },
                "marker": {
                    "color": [
                        "#2ecc71" if val >= 0 else "#e74c3c"
                        for val in filtered_data["Change"]
                    ],
                    "size": 8,
                },
                "fill": "tozeroy",
                "fillcolor": "rgba(46, 204, 113, 0.1)",
            }
        ],
        "layout": {
            "paper_bgcolor": "#fffdf5",
            "plot_bgcolor": "#fffdf5",
            "margin": {"l": 50, "r": 30, "t": 10, "b": 50},
            "xaxis": {
                "showgrid": False,
                "zeroline": False,
                "title": "",
                "tickfont": {"size": 12, "color": "#555"},
                "tickformat": "%b %d",  # Format as "Mar 09"
                "tickangle": -45,
            },
            "yaxis": {
                "showgrid": True,
                "gridcolor": "#f0f0f0",
                "zeroline": True,
                "zerolinecolor": "#e0e0e0",
                "title": "% Change",
                "titlefont": {"size": 14, "color": "#555"},
                "ticksuffix": "%",
                "tickfont": {"size": 12, "color": "#555"},
            },
            "hovermode": "closest",
            "hoverlabel": {
                "bgcolor": "white",
                "font": {"color": "#333"},
                "bordercolor": "#ddd",
            },
        },
    }

    return figure


# Layout
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Change in seated diners by week, 2025 vs. 2024"),
                        html.P(
                            "This graph measures the weekly change in seated diners from online reservations for 2025 vs. 2024. "
                            "Hover over any given date to see how 2025 compares to the respective week in 2024. "
                            "For example, in the US on the week ending on January 6, 2025, seated diners were up 25% compared to "
                            "the respective week of the year in 2024."
                        ),
                    ],
                    className="container",
                )
            ],
            className="header",
        ),
        # Main content
        html.Div(
            [
                # Region dropdown
                html.Div(
                    [
                        dcc.Dropdown(
                            id="region-select",
                            options=[
                                {"label": region, "value": region} for region in regions
                            ],
                            value="Global",
                            style={"width": "200px", "display": "inline-block"},
                            clearable=False,
                        ),
                    ],
                    className="dropdown-container",
                ),
                # Chart container
                html.Div(
                    [
                        # Legend
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            style={
                                                "width": "30px",
                                                "height": "4px",
                                                "backgroundColor": "#e74c3c",
                                                "marginRight": "8px",
                                            }
                                        ),
                                        html.Div(
                                            "Decline",
                                            style={
                                                "fontSize": "0.9em",
                                                "color": "#555",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginLeft": "20px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            style={
                                                "width": "30px",
                                                "height": "4px",
                                                "backgroundColor": "#2ecc71",
                                                "marginRight": "8px",
                                            }
                                        ),
                                        html.Div(
                                            "Growth",
                                            style={
                                                "fontSize": "0.9em",
                                                "color": "#555",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginLeft": "20px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "2025 vs. 2024",
                                            style={
                                                "fontSize": "0.9em",
                                                "color": "#555",
                                            },
                                        )
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginLeft": "20px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "flex-end",
                                "marginBottom": "15px",
                            },
                        ),
                        # Chart
                        dcc.Graph(
                            id="weekly-graph",
                            figure=create_figure(plot_df),
                            config={"displayModeBar": False},
                            style={"height": "400px"},
                        ),
                    ],
                    className="chart-container",
                ),
            ],
            className="container",
        ),
    ]
)


# Add callback to update the graph based on region selection
@app.callback(
    dash.dependencies.Output("weekly-graph", "figure"),
    [dash.dependencies.Input("region-select", "value")],
)
def update_graph(selected_region):
    # Filter data for the selected region
    filtered_data = plot_df[plot_df["Region"] == selected_region]

    # Create a custom figure with the filtered data
    figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Change"],
                "type": "scatter",
                "mode": "lines+markers",
                "name": selected_region,
                "line": {
                    "color": [
                        "#2ecc71" if val >= 0 else "#e74c3c"
                        for val in filtered_data["Change"]
                    ],
                    "width": 2,
                    "shape": "spline",
                },
                "marker": {
                    "color": [
                        "#2ecc71" if val >= 0 else "#e74c3c"
                        for val in filtered_data["Change"]
                    ],
                    "size": 8,
                },
                "fill": "tozeroy",
                "fillcolor": "rgba(46, 204, 113, 0.1)",
            }
        ],
        "layout": {
            "paper_bgcolor": "#fffdf5",
            "plot_bgcolor": "#fffdf5",
            "margin": {"l": 50, "r": 30, "t": 10, "b": 50},
            "xaxis": {
                "showgrid": False,
                "zeroline": False,
                "title": "",
                "tickfont": {"size": 12, "color": "#555"},
                "tickformat": "%b %d",  # Format as "Mar 09"
                "tickangle": -45,
            },
            "yaxis": {
                "showgrid": True,
                "gridcolor": "#f0f0f0",
                "zeroline": True,
                "zerolinecolor": "#e0e0e0",
                "title": "% Change",
                "titlefont": {"size": 14, "color": "#555"},
                "ticksuffix": "%",
                "tickfont": {"size": 12, "color": "#555"},
            },
            "hovermode": "closest",
            "hoverlabel": {
                "bgcolor": "white",
                "font": {"color": "#333"},
                "bordercolor": "#ddd",
            },
        },
    }

    return figure


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
