import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html  # Add this import

def create_chart_figure(df, signals, indicators, predictions=None):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Main candlestick chart
    fig.add_candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        row=1, col=1
    )
    
    # Add Bollinger Bands if selected
    if "BB" in indicators:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_high'], name='BB Upper',
                      line=dict(color='gray', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_low'], name='BB Lower',
                      line=dict(color='gray', dash='dash')),
            row=1, col=1
        )
    
    # Add LSTM predictions if selected
    if "LSTM" in indicators and predictions is not None:
        fig.add_trace(
            go.Scatter(x=df.index[-len(predictions):], y=predictions.flatten(),
                      name='LSTM Prediction', line=dict(color='yellow')),
            row=1, col=1
        )
    
    # Add trading signals
    entry_points = df[signals['entry']]
    exit_points = df[signals['exit']]
    stop_points = df[signals['stop_loss']]
    
    fig.add_trace(
        go.Scatter(x=entry_points.index, y=entry_points['Low']*0.99,
                  mode='markers', name='Entry',
                  marker=dict(symbol='triangle-up', size=10, color='green')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=exit_points.index, y=exit_points['High']*1.01,
                  mode='markers', name='Exit',
                  marker=dict(symbol='triangle-down', size=10, color='blue')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=stop_points.index, y=stop_points['Low']*0.99,
                  mode='markers', name='Stop Loss',
                  marker=dict(symbol='x', size=10, color='red')),
        row=1, col=1
    )
    
    # Add RSI if selected
    if "RSI" in indicators:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI'),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # Add MACD if selected
    if "MACD" in indicators:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'], name='MACD'),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_signal'], name='Signal'),
            row=3, col=1
        )
    
    # Update layout
    fig.update_layout(
        title=f'{df.index[0].strftime("%Y-%m-%d")} Trading Analysis',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        height=800
    )
    
    return fig

def create_price_chart(df, symbol, signals):    # Added signals parameter
    fig = go.Figure()
    
    fig.add_candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    )
    
    # Add Bollinger Bands if available
    if 'BB_high' in df.columns and 'BB_low' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_high'], name='BB Upper',
                      line=dict(color='gray', dash='dash'))
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_low'], name='BB Lower',
                      line=dict(color='gray', dash='dash'))
        )
    
    # Add trading signals
    entry_points = df[signals['entry']]
    exit_points = df[signals['exit']]
    stop_points = df[signals['stop_loss']]
    
    fig.add_trace(
        go.Scatter(x=entry_points.index, y=entry_points['Low']*0.99,
                  mode='markers', name='Entry',
                  marker=dict(symbol='triangle-up', size=10, color='green'))
    )
    
    fig.add_trace(
        go.Scatter(x=exit_points.index, y=exit_points['High']*1.01,
                  mode='markers', name='Exit',
                  marker=dict(symbol='triangle-down', size=10, color='blue'))
    )
    
    fig.add_trace(
        go.Scatter(x=stop_points.index, y=stop_points['Low']*0.99,
                  mode='markers', name='Stop Loss',
                  marker=dict(symbol='x', size=10, color='red'))
    )
    
    fig.update_layout(
        title=f'{symbol} Price Chart',
        yaxis_title='Price',
        template='plotly_dark',
        height=600
    )
    
    return fig

def create_indicator_chart(df, indicators):
    fig = make_subplots(rows=len(indicators) if indicators else 1, cols=1, 
                        shared_xaxes=True, vertical_spacing=0.05)
    
    row = 1
    for indicator in indicators or []:
        if indicator == "rsi":
            fig.add_trace(
                go.Scatter(x=df.index, y=df['RSI'], name='RSI'),
                row=row, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=row, col=1)
            row += 1
            
        elif indicator == "macd":
            fig.add_trace(
                go.Scatter(x=df.index, y=df['MACD'], name='MACD'),
                row=row, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['MACD_signal'], name='Signal'),
                row=row, col=1
            )
            row += 1
    
    fig.update_layout(
        height=200 * (len(indicators) if indicators else 1),
        template='plotly_dark'
    )
    
    return fig

def create_performance_metrics(df):
    if len(df) < 2:
        return html.Div([
            html.H4("Performance Metrics"),
            html.P("Insufficient data to calculate performance metrics.")
        ])
    
    return html.Div([
        html.H4("Performance Metrics"),
        html.P(f"Current Price: ${df['Close'].iloc[-1]:.2f}"),
        html.P(f"Daily Change: {((df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100):.2f}%"),
        html.P(f"Volume: {df['Volume'].iloc[-1]:,.0f}")
    ])