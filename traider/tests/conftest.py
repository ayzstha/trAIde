import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@pytest.fixture
def sample_market_data():
    """Generate sample market data for testing"""
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    data = pd.DataFrame({
        'Open': np.random.uniform(100, 150, len(dates)),
        'High': np.random.uniform(120, 170, len(dates)),
        'Low': np.random.uniform(90, 140, len(dates)),
        'Close': np.random.uniform(100, 160, len(dates)),
        'Volume': np.random.uniform(1000000, 5000000, len(dates))
    }, index=dates)
    return data