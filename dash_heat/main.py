# import dataiku
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

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
                padding: 0 10px;
            }
            .dropdown-container {
                margin: 30px 0;
                text-align: left;
            }
            .chart-container {
                background-color: #fffdf5;
                border-radius: 8px;
                padding: 10px;
                margin-top: 20px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                overflow-x: auto;
                white-space: nowrap;
            }
            .scrollable-container {
                overflow-x: auto;
                width: 100%;
            }
            /* Custom styling for heatmap cells */
            .js-plotly-plot .heatmap .textpoint {
                font-size: 11px !important;
            }
            /* Reduce the height of heatmap cells */
            .js-plotly-plot .heatmap .point {
                transform: scale(1, 0.85);
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
df = pd.read_csv("data.csv", header=0)

# Prepare data for table and graph
dates = df.columns[1:]  # Exclude region column
regions = df.iloc[:, 0].tolist()  # First column as regions

# Clean the data to ensure numeric values (remove % signs)
for col in dates:
    df[col] = df[col].str.replace("%", "").astype(float)

# Create a copy of the original dataframe for the heatmap
heatmap_df = df.copy()

# Convert to long format for plotting
plot_df = df.copy()
plot_df = plot_df.melt(id_vars=["Region"], var_name="Date", value_name="Change")

# Add the current year to the date columns for proper parsing
current_year = datetime.now().year
plot_df["Date"] = plot_df["Date"] + f"/{current_year}"

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


# Function to create a heatmap figure
def create_heatmap(view_type="daily"):
    if view_type == "daily":
        # Use the original data for daily view
        z_data = heatmap_df.iloc[:, 1:].values
        x_labels = [d for d in dates]
    else:
        # Aggregate data by month for monthly view
        monthly_pivot = monthly_df.pivot(
            index="Region", columns="Month", values="Change"
        )
        z_data = monthly_pivot.values
        x_labels = [
            datetime.strptime(m, "%Y-%m").strftime("%b %Y")
            for m in monthly_pivot.columns
        ]

    # Create a custom colorscale
    colorscale = [
        [0, "#e74c3c"],  # Red for negative values
        [0.5, "#ffffff"],  # White for zero
        [1, "#2ecc71"],  # Green for positive values
    ]

    # Create the heatmap figure
    fig = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=regions,
            colorscale=colorscale,
            zmin=-15,  # Set minimum value for color scale
            zmax=30,  # Set maximum value for color scale
            zmid=0,  # Set the midpoint of the color scale to 0
            text=[[f"{val}%" for val in row] for row in z_data],
            texttemplate="%{text}",
            textfont={"size": 11, "color": "black"},  # Reduced font size
            hoverinfo="text",
            hovertext=[
                [f"{regions[i]}, {x_labels[j]}: {val}%" for j, val in enumerate(row)]
                for i, row in enumerate(z_data)
            ],
        )
    )

    # Calculate width based on number of columns (dates)
    # Set a minimum width per column (in pixels)
    column_width = 80  # Width per column in pixels
    total_width = max(
        1200, len(x_labels) * column_width
    )  # Ensure minimum width of 1200px

    # Calculate a more compact height based on number of rows
    row_height = 30  # Reduced height per row in pixels
    total_height = max(350, len(regions) * row_height + 80)  # Reduced padding

    # Update layout
    fig.update_layout(
        paper_bgcolor="#fffdf5",
        plot_bgcolor="#fffdf5",
        margin={"l": 10, "r": 30, "t": 50, "b": 20},  # Further reduced bottom margin
        xaxis={
            "side": "top",
            "title": {
                "text": "MONTH/DAY",
                "font": {
                    "size": 14,
                    "color": "#333",
                    "family": "Helvetica Neue",
                    "weight": "bold",
                },
            },
            "tickfont": {
                "size": 12,
                "color": "#333",
                "weight": "bold",
            },
            "tickangle": 0,
            "constrain": "domain",  # Ensure x-axis is not compressed
        },
        yaxis={
            "title": "",
            "tickfont": {
                "size": 11,
                "color": "#333",
                "weight": "bold",
            },  # Reduced font size
            "autorange": "reversed",  # Reverse the y-axis to match the image
            "scaleanchor": False,  # Prevent y-axis from scaling with x-axis
            "ticklen": 2,  # Shorter tick marks
        },
        height=total_height,  # Dynamic height based on number of rows
        width=total_width,
    )

    return fig


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
                # Dropdown container
                html.Div(
                    [
                        # Country dropdown
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="country-select",
                                    options=[{"label": "Country", "value": "country"}],
                                    value="country",
                                    style={
                                        "width": "200px",
                                        "paddingRight": "5px",
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
                        # View dropdown
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
                                        "paddingRight": "5px",
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
                # Heatmap container
                html.Div(
                    [
                        # Heatmap
                        html.Div(
                            dcc.Graph(
                                id="heatmap-chart",
                                figure=create_heatmap("daily"),
                                config={"displayModeBar": False},
                                style={
                                    "height": "auto",  # Changed from fixed height to auto
                                    "minWidth": "100%",
                                },
                            ),
                            className="scrollable-container",
                        ),
                    ],
                    className="chart-container",
                ),
            ],
            className="container",
        ),
    ]
)


# Callback to update heatmap based on view selection
@app.callback(
    Output("heatmap-chart", "figure"),
    [Input("view-select", "value")],
)
def update_heatmap(view_type):
    return create_heatmap(view_type)


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
