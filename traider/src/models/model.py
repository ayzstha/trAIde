import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

class TradingModel:
    def __init__(self, sequence_length: int = 60):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()
        
    def build_model(self, input_shape: Tuple[int, int]) -> None:
        """
        Build LSTM model architecture
        
        Args:
            input_shape: (sequence_length, n_features)
        """
        self.model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1)
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mean_squared_error'
        )
        
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for LSTM model
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            X: Features array
            y: Target array
        """
        # Create features
        features = self._engineer_features(data)
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Create sequences
        X, y = [], []
        for i in range(len(scaled_features) - self.sequence_length):
            X.append(scaled_features[i:(i + self.sequence_length)])
            y.append(scaled_features[i + self.sequence_length, 0])  # Predict next close price
            
        return np.array(X), np.array(y)
    
    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create technical indicators as features
        """
        df = data.copy()
        
        # Price features
        df['Returns'] = df['Close'].pct_change()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        # Volume features
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        
        # Volatility features
        df['ATR'] = self._calculate_atr(df)
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
             epochs: int = 50, batch_size: int = 32, validation_split: float = 0.2):
        """Train the model"""
        if self.model is None:
            self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
            
        return self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        return self.model.predict(X)