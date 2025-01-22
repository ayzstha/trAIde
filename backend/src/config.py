import os

# Disable oneDNN custom operations
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class TradingConfig:
    # Data parameters
    DEFAULT_TICKER = 'AAPL'
    TIMEFRAMES = {
        '1m': '1 Minute',
        '5m': '5 Minutes',
        '15m': '15 Minutes',
        '1h': '1 Hour',
        '1d': '1 Day',
        '5d': '5 Days',
        '1mo': '1 Month'
    }
    
    # Technical indicators
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STD = 2
    
    # Trading parameters
    RISK_REWARD_RATIO = 2.0
    STOP_LOSS_PCT = 0.02
    TAKE_PROFIT_PCT = 0.04
    
    # LSTM model parameters
    SEQUENCE_LENGTH = 10
    TRAIN_TEST_SPLIT = 0.8
    EPOCHS = 50
    BATCH_SIZE = 32
    
    # Backtesting
    INITIAL_CAPITAL = 100000.0
    
    # UI Settings
    CHART_HEIGHT = 800
    UPDATE_INTERVAL = 60000  # 1 minute in milliseconds