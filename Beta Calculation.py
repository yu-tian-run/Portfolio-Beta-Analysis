import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, tuple, Optional


class PorfolioBetaCalc:

    def __init__(self, benchmark: str = "^GSPC")
        self.benchmarke = benchmark
        self.benchmark_data = None
        self.stock_data = {}
        self.portfolio_stocks = {}

    def fetch_benchmark_beta(self, ticker: str, period: str = "2y") -> pd.DataFrame:
        # fetch S&P 500 data as benchmark
        self.benchmark_data = yf.download(self.benchmark, start=start_date, end=end_date)
        self.benchmark_data['Returns'] = self.benchmark_data['Adj Close'].pct_change()
        self.benchmark_data.dropna(inplace=True)