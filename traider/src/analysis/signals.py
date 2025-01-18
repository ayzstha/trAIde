from typing import Dict, Optional
import pandas as pd
import numpy as np
from .technical import TechnicalAnalyzer
from .patterns import PatternRecognition

class SignalGenerator:
    def __init__(self):
        self.tech_analyzer = TechnicalAnalyzer()
        self.pattern_recognizer = PatternRecognition()
        
    def generate_signals(self, data: pd.DataFrame, account_value: float = 100000, 
                        risk_percent: float = 1.0) -> Dict[str, any]:
        """Generate trading signals and risk parameters"""
        # Calculate indicators
        rsi = self.tech_analyzer.calculate_rsi(data)
        macd, signal_line = self.tech_analyzer.calculate_macd(data)
        trend = self.pattern_recognizer.identify_trend(data)
        
        # Generate signals
        entry_signal = self._generate_entry_signal(data, rsi, macd, signal_line)
        exit_signal = self._generate_exit_signal(data, rsi, macd, signal_line)
        
        # Calculate risk levels
        current_price = data['Close'].iloc[-1]
        stop_loss = self._calculate_stop_loss(data, trend)
        take_profit = self._calculate_take_profit(current_price, stop_loss)
        position_size = self._calculate_position_size(account_value, risk_percent, 
                                                    current_price, stop_loss)
        
        return {
            "entry": entry_signal,
            "exit": exit_signal,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size,
            "trend": trend
        }
    
    def _generate_entry_signal(self, data: pd.DataFrame, rsi: pd.Series, 
                             macd: pd.Series, signal: pd.Series) -> Optional[str]:
        """Generate entry signals based on indicators"""
        volume_confirmed = data['Volume'].iloc[-1] > data['Volume'].rolling(20).mean().iloc[-1]
        
        if rsi.iloc[-1] < 30 and macd.iloc[-1] > signal.iloc[-1] and volume_confirmed:
            return "LONG"
        elif rsi.iloc[-1] > 70 and macd.iloc[-1] < signal.iloc[-1] and volume_confirmed:
            return "SHORT"
        return None
    
    def _generate_exit_signal(self, data: pd.DataFrame, rsi: pd.Series, 
                         macd: pd.Series, signal: pd.Series) -> Optional[str]:
        """
        Generate exit signals based on technical indicators
        
        Args:
            data: OHLCV price data
            rsi: Relative Strength Index
            macd: MACD line
            signal: Signal line
        
        Returns:
            str or None: Exit signal type
        """
        # Add volume confirmation
        volume_ma = data['Volume'].rolling(window=20).mean()
        high_volume = data['Volume'].iloc[-1] > volume_ma.iloc[-1]

        if (rsi.iloc[-1] > 70 or macd.iloc[-1] < signal.iloc[-1]) and high_volume:
            return "EXIT_LONG"
        elif (rsi.iloc[-1] < 30 or macd.iloc[-1] > signal.iloc[-1]) and high_volume:
            return "EXIT_SHORT"
        return None

    def _calculate_stop_loss(self, data: pd.DataFrame, trend: str, 
                        atr_multiple: float = 2.0) -> Dict[str, float]:
        """
        Calculate initial and trailing stop loss levels
        
        Args:
            data: OHLCV price data
            trend: Current trend direction
            atr_multiple: ATR multiplier for stop calculation
        
        Returns:
            Dict with initial and trailing stop levels
        """
        atr = self._calculate_atr(data)
        current_price = data['Close'].iloc[-1]
        
        initial_stop = (current_price - (atr * atr_multiple) if trend == "UPTREND" 
                       else current_price + (atr * atr_multiple))
        
        trailing_stop = self._calculate_trailing_stop(data, trend, atr_multiple)
        
        return {
            "initial_stop": initial_stop,
            "trailing_stop": trailing_stop,
            "risk_amount": abs(current_price - initial_stop)
        }

    def _calculate_trailing_stop(self, data: pd.DataFrame, trend: str, 
                           atr_multiple: float = 2.0) -> float:
        """Calculate trailing stop loss level"""
        atr = self._calculate_atr(data)
        if trend == "UPTREND":
            return data['High'].rolling(window=10).max() - (atr * atr_multiple)
        return data['Low'].rolling(window=10).min() + (atr * atr_multiple)

    def _calculate_position_size(self, account_value: float, risk_percent: float, 
                               entry_price: float, stop_loss: float) -> int:
        """Calculate position size based on risk"""
        risk_amount = account_value * (risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)
        return int(risk_amount / price_risk)

    def _calculate_take_profit(self, entry_price: float, stop_loss: float, 
                             risk_reward: float = 2.0) -> float:
        """Calculate take profit level"""
        risk = abs(entry_price - stop_loss)
        return entry_price + (risk * risk_reward) if entry_price > stop_loss else entry_price - (risk * risk_reward)
    
    def calculate_position_size(self, account_value: float, risk_per_trade: float, 
                          stop_loss: float, current_price: float) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            account_value: Total account value
            risk_per_trade: Maximum risk percentage per trade
            stop_loss: Stop loss price
            current_price: Current asset price
        
        Returns:
            int: Number of shares/contracts to trade
        """
        risk_amount = abs(current_price - stop_loss)
        max_risk_amount = account_value * (risk_per_trade / 100)
        position_size = int(max_risk_amount / risk_amount)
        return position_size

    def calculate_take_profit(self, entry_price: float, stop_loss: float, 
                        risk_reward: float = 2.0) -> float:
        """Calculate take profit level based on risk-reward ratio"""
        risk = abs(entry_price - stop_loss)
        return entry_price + (risk * risk_reward) if entry_price > stop_loss else entry_price - (risk * risk_reward)