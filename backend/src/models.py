import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from .config import TradingConfig as cfg  # Ensure config is imported

class LSTMPredictor:
    def __init__(self, sequence_length=cfg.SEQUENCE_LENGTH):    # Use config
        self.sequence_length = sequence_length
        self.model = self._build_model()
        self.scaler = MinMaxScaler()
        
    def _build_model(self):
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.sequence_length, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def prepare_data(self, data):
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        X, y = [], []
        
        for i in range(len(scaled_data) - self.sequence_length):
            X.append(scaled_data[i:(i + self.sequence_length), 0])
            y.append(scaled_data[i + self.sequence_length, 0])
            
        return np.array(X), np.array(y)
    
    def train(self, data, epochs=cfg.EPOCHS, batch_size=cfg.BATCH_SIZE):    # Use config
        X, y = self.prepare_data(data)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
        
    def predict(self, data):
        X, _ = self.prepare_data(data)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        predictions = self.model.predict(X)
        return self.scaler.inverse_transform(predictions.reshape(-1, 1))

class TradingStrategy:
    def __init__(self, risk_ratio=cfg.RISK_REWARD_RATIO, stop_loss_pct=cfg.STOP_LOSS_PCT):    # Use config
        self.risk_ratio = risk_ratio
        self.stop_loss_pct = stop_loss_pct
        
    def calculate_signals(self, df):
        df = df.copy()
        
        # ATR for volatility-based stops
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        # Stochastic Oscillator
        low_min = df['Low'].rolling(14).min()
        high_max = df['High'].rolling(14).max()
        df['Stoch_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
        df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()
        
        # Volume indicators
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        signals = pd.DataFrame(index=df.index)
        
        # Entry conditions
        signals['entry'] = (
            (df['RSI'] < 30) & 
            (df['MACD'] > df['MACD_signal']) & 
            (df['Stoch_K'] < 20) & 
            (df['Close'] > df['VWAP'])
        )
        
        # Exit conditions
        signals['exit'] = (
            (df['RSI'] > 70) | 
            (df['Close'] > df['BB_high']) | 
            (df['Stoch_K'] > 80) |
            (df['MACD'] < df['MACD_signal'])
        )
        
        # Stop loss
        signals['stop_loss'] = (
            (df['Close'] < df['BB_low']) | 
            (df['Close'] < df['Close'].shift(1) - df['ATR'] * 2)
        )
        
        return signals, df

def backtest_strategy(data, signals, initial_capital=cfg.INITIAL_CAPITAL):
    position = 0
    balance = initial_capital
    trades = []
    
    for i in range(len(data)):
        if signals['entry'].iloc[i] and position == 0:
            position = balance / data['Close'].iloc[i]
            entry_price = data['Close'].iloc[i]
            entry_date = data.index[i]
        
        elif (signals['exit'].iloc[i] or signals['stop_loss'].iloc[i]) and position > 0:
            balance = position * data['Close'].iloc[i]
            exit_price = data['Close'].iloc[i]
            exit_date = data.index[i]
            returns = (exit_price - entry_price) / entry_price * 100
            trades.append({
                'entry_date': entry_date,
                'exit_date': exit_date,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'returns': returns
            })
            position = 0
    
    if trades:
        trades_df = pd.DataFrame(trades)
        performance = {
            'total_trades': len(trades),
            'winning_trades': len(trades_df[trades_df['returns'] > 0]),
            'avg_return': trades_df['returns'].mean(),
            'max_return': trades_df['returns'].max(),
            'min_return': trades_df['returns'].min(),
            'final_balance': balance,
            'total_return': (balance - initial_capital) / initial_capital * 100
        }
    else:
        performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'avg_return': 0,
            'max_return': 0,
            'min_return': 0,
            'final_balance': balance,
            'total_return': 0
        }
    
    return trades, performance