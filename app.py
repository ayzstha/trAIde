import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from backend.src.data_service import fetch_data, calculate_indicators
from frontend.src.charts import create_price_chart, create_indicator_chart, create_performance_metrics
from backend.src.models import TradingStrategy  # Add this import

def create_chart_area():
    return dbc.Col([
        dcc.Graph(id="price-chart"),
        dcc.Graph(id="indicator-chart"),
        html.Div(id="performance-metrics", className="mt-3"),  # Added performance metrics div
        dcc.Interval(id="interval-component"),
        html.Div(id="update-status")
    ], width=9)

def create_sidebar_controls():
    return dbc.Col([
        html.Div([
            html.H4("Controls", className="mb-3"),
            dbc.Input(
                id="symbol-input",
                placeholder="Enter stock symbol...",
                className="mb-3"
            ),
            dcc.Dropdown(
                id="timeframe-select",
                options=[
                    {"label": "1D", "value": "1d"},
                    {"label": "5D", "value": "5d"},
                    {"label": "1M", "value": "1mo"}
                ],
                className="mb-3"
            ),
            dcc.Dropdown(
                id="interval-select",
                options=[
                    {"label": "1 min", "value": "1m"},
                    {"label": "5 min", "value": "5m"},
                    {"label": "15 min", "value": "15m"},
                    {"label": "15 min", "value": "1h"},
                    {"label": "15 min", "value": "1d"}
                ],
                className="mb-3"
            ),
            dcc.Checklist(
                id="technical-indicators",
                options=[
                    {"label": "RSI", "value": "rsi"},
                    {"label": "MACD", "value": "macd"},
                    {"label": "BB", "value": "bollinger"}
                ],
                className="mb-3"
            ),
            dbc.Button("Update", id="update-button", color="primary", className="w-100")
        ], className="p-3 bg-light rounded")
    ], width=3)

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="trAIde - AI Trading Tool",          # Set browser tab title
)

def create_layout():
    return dbc.Container([
        html.Title("trAIde - AI Trading Tool"),
        html.H1("trAIde - AI Trading Tool", className="mb-4"),
        dbc.Row([
            create_sidebar_controls(),
            create_chart_area()
        ])
    ], fluid=True)

@app.callback(
    [Output("price-chart", "figure"),
     Output("indicator-chart", "figure"),
     Output("performance-metrics", "children")],
    [Input("symbol-input", "value"),
     Input("timeframe-select", "value"),
     Input("interval-select", "value"),       # Added interval input
     Input("update-button", "n_clicks")],
    [State("technical-indicators", "value")],
    prevent_initial_call=True
)
def update_dashboard(symbol, timeframe, interval, n_clicks, indicators):
    ctx = callback_context
    if not ctx.triggered or not symbol:
        return {}, {}, []
    
    try:
        # Fetch and process data with both period and interval
        df = fetch_data(symbol, timeframe, interval)
        df = calculate_indicators(df)
        
        if df.empty or len(df) < 2:
            return {}, {}, [html.Div("Error: Insufficient data retrieved.")]
        
        # Calculate trading signals
        strategy = TradingStrategy()
        signals, df = strategy.calculate_signals(df)
        
        # Create charts and metrics with signals
        price_fig = create_price_chart(df, symbol, signals)
        indicator_fig = create_indicator_chart(df, indicators)
        metrics = create_performance_metrics(df)
        
        return price_fig, indicator_fig, metrics
    except Exception as e:
        return {}, {}, [html.Div(f"Error: {str(e)}")]

if __name__ == '__main__':
    app.layout = create_layout()
    app.run_server(debug=True, port=8050)