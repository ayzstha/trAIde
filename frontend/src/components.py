import dash_bootstrap_components as dbc
from dash import html, dcc
from backend.src.config import TradingConfig as cfg

def create_sidebar_controls():
    """Create the sidebar control panel"""
    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.H4("Controls", className="card-title"),
                html.Label("Ticker Symbol"),
                dbc.Input(id="ticker-input", value=cfg.DEFAULT_TICKER, type="text"),
                
                html.Label("Timeframe"),
                dcc.Dropdown(
                    id="timeframe-select",
                    options=[{"label": v, "value": k} for k, v in cfg.TIMEFRAMES.items()],
                    value="1d"
                ),
                
                html.Label("Indicators"),
                dcc.Checklist(
                    id="indicator-checklist",
                    options=[
                        {"label": "RSI", "value": "RSI"},
                        {"label": "MACD", "value": "MACD"},
                        {"label": "Bollinger Bands", "value": "BB"},
                        {"label": "LSTM Predictions", "value": "LSTM"}
                    ],
                    value=["RSI", "MACD", "BB"]
                ),
                
                html.Label("Risk/Reward Ratio"),
                dbc.Input(
                    id="risk-reward-input",
                    type="number",
                    value=cfg.RISK_REWARD_RATIO,
                    min=0.1,
                    step=0.1
                ),
                
                html.Label("Stop Loss %"),
                dbc.Input(
                    id="stop-loss-input",
                    type="number",
                    value=cfg.STOP_LOSS_PCT * 100,
                    min=0.1,
                    step=0.1
                ),
                
                dbc.Button("Update", id="update-button", color="primary", className="mt-3"),
            ])
        ])
    ], width=3)

def create_chart_area():
    """Create the main chart area"""
    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(id="price-chart", style={"height": cfg.CHART_HEIGHT}),
                html.Div(id="performance-metrics", className="mt-3")
            ])
        ])
    ], width=9)