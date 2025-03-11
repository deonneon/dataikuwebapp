# import dataiku
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime

# Initialize Dash app with custom styles
app = dash.Dash(
    __name__,
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
                padding: 20px 20px;
            }
            .header h1 {
                font-size: 2em;
                color: #333;
                margin-bottom: 10px;
                font-weight: 600;
            }
            .header p {
                font-size: 0.9em;
                color: #555;
                max-width: 800px;
                margin: 0;
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
            .dash-table-container {
                margin-top: 20px;
                border-radius: 8px;
                overflow: hidden;
            }
            .dash-spreadsheet-container {
                border-radius: 8px;
                overflow: hidden;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
            .dash-spreadsheet-inner th {
                background-color: #fffdf5 !important;
                color: #333 !important;
                font-weight: 600 !important;
                border-bottom: 2px solid #eaeaea !important;
                text-align: center !important;
            }
            .dash-spreadsheet-inner td {
                background-color: #fffdf5 !important;
                color: #333 !important;
                border-bottom: 1px solid #eaeaea !important;
                text-align: center !important;
            }
            .dash-cell-value {
                text-align: center !important;
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
df = pd.read_csv("dash/data.csv", header=0)

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

# Create a monthly aggregated dataframe
monthly_df = plot_df.copy()
monthly_df["Month"] = monthly_df["Date"].dt.strftime("%Y-%m")
monthly_df = (
    monthly_df.groupby(["Region", "Month"]).agg({"Change": "mean"}).reset_index()
)
monthly_df["Date"] = pd.to_datetime(
    monthly_df["Month"] + "-15"
)  # Set to middle of month for display


# Function to create the figure with ExampleDash styling
def create_figure(data, selected_region, view_type="daily"):
    # Filter data for the selected region
    if view_type == "daily":
        filtered_data = data[data["Region"] == selected_region]
    else:  # monthly view
        filtered_data = monthly_df[monthly_df["Region"] == selected_region]

    # Create a custom figure
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
                "tickformat": (
                    "%b %d" if view_type == "daily" else "%b %Y"
                ),  # Format based on view
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
                        html.H1(
                            "Change in seated diners by month / day, 2025 vs. 2024"
                        ),
                        html.P(
                            "This table measures the volume of seated diners from online reservations on a daily/monthly basis in 2025 vs. "
                            "2024. For example, in Los Angeles on January 4, 2025, seated diners were up 3% compared to 2024. In the "
                            "monthly view, data for the current month shows the YoY change in seated diners for the month-to-date. For "
                            "example, if the date is January 10, 2025, the data compares January 1 - 10, 2025 to the same range in 2024."
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
                        # Dropdown container with relative positioning
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="region-select",
                                    options=[
                                        {"label": region, "value": region}
                                        for region in regions
                                    ],
                                    value="Global",
                                    style={
                                        "width": "200px",
                                        "paddingRight": "5px",  # Add padding for the caret
                                    },
                                    clearable=False,
                                ),
                            ],
                            style={
                                "position": "relative",
                                "display": "inline-block",
                                "marginRight": "20px",
                            },
                        ),
                        # View dropdown container with relative positioning
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="view-select",
                                    options=[
                                        {"label": "Daily", "value": "daily"},
                                        {"label": "Monthly", "value": "monthly"},
                                    ],
                                    value="daily",
                                    style={
                                        "width": "200px",
                                        "paddingRight": "5px",  # Add padding for the caret
                                    },
                                    clearable=False,
                                ),
                            ],
                            style={
                                "position": "relative",
                                "display": "inline-block",
                            },
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
                            id="weekly-chart",
                            figure=create_figure(plot_df, "Global", "daily"),
                            config={"displayModeBar": False},
                            style={"height": "400px"},
                        ),
                        # Table (hidden by default)
                        html.Div(id="table-container", style={"display": "none"}),
                    ],
                    className="chart-container",
                ),
            ],
            className="container",
        ),
    ]
)


# Callback to update chart based on region and view selection
@app.callback(
    Output("weekly-chart", "figure"),
    [Input("region-select", "value"), Input("view-select", "value")],
)
def update_chart(selected_region, view_type):
    return create_figure(plot_df, selected_region, view_type)


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
