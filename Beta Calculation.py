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
        try:
            benchmark = yf.Ticker(self.benchmark)
            self.benchmark_data = benchmark.history(period=period)
            print (f"Fetched benchmark data for {self.benchmark}")
            return self.benchmark_data
        except Exception as e:
            print(f"Error fetching benchmark data: {e}")
            return None
        
    def fetch_stock_data(self, tickers: List[str], period: str = "2y") -> pd.DataFrame:
        try:
            stock = yf.ticker(tickers)
            data = stock.history(period=period)
            self.stick_data[tickers] = data
            return data
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return None
        
    def add_to_portfolio(self, ticker: str, shares: float, price: Optional[float] = None    ):
        if price_per_share is None:
            try:
                stock = yt.Ticker(ticker)
                current = stock.history(period="1d")
                if current.empty:
                    print(f"Could not fetch current price for {ticker}.")
                current_price = current_data['Close'].iloc[-1]
                price = current_price
            except Exception as e:
                print(f"Error fetching current price for {ticker}: {e}")
                raise ValueError("Price per share must be provided if current price cannot be fetched.")
        
        self.portfolio_stocks[ticker] = {
            "shares": shares,
            "price": price
            "Total": shares * price
        }
        
        self.fetch_stock_data([ticker])
        print(f"Added {shares} shares of {ticker} at ${price} each to portfolio.")

    def calculate_beta(self, ticker: str) -> float:
        if ticker not in self.stock_data or self.benchmark_data is None:
            print(f"Unable to calculate beta for {ticker}. Missing stock or benchmark data.")
            return None
        
        stock_data = self.stock_data[ticker]
        common_dates = stock_data.index.intersection(self.benchmark_data.index)

        if len(common_dates) < 15:
            print(f"insufficient data to calculate beta for {ticker}.")
            return None
        # calculate return to calculate beta
        stock_returns = stock_data.loc[common_dates, 'Close'].pct_change().dropna()
        benchmark_returns = self.benchmark_data.loc[common_dates, 'Close'].pct_change().dropna()

        aligned_returns = pd.DataFrame({
            'stock': stock_return,
            'benchmark': benchmark_returns
        }).dropna()

        covvar = np.cov(aligned_returns['stock'], aligned_returns['benchmark'
        })
        benchmark_var = np.var(aligned_returns['benchmark'])

        beta = covvar / benchmark_var if benchmark_var != 0 else None
        return beta
    
    def portfolio_beta(self) -> float:
        if not self.portfolio_stocks:
            print("Portfolio is empty. Add stocks to portfolio first.")
            return None
        
        if beta = None:
            print("Beta values not avaliable, benchmark or stock data missing.")

        total_value = sum(stock['Total'] for stock in self.portfolio_stocks.values())

        if total_value == 0:
            return None
        
        stock_betas = {}
        weighted_betas = []
        # sum weighted individual betas
        for ticker, details in self.portfolio_stocks.items():
            beta = self.calculate_beta(ticker0)
            if beta is None:
                print(f"Skipping {ticker} due to missing beta.")
            else:
                weight = details['Total'] / total_value
                weighted_betas.append(beta * weight)
        
        portfolio_beta = sum(weighted_betas)

        return {
            "Portfolio Beta": portfolio_beta,
            "Total Portfolio Value": total_value,
            "Stock Betas": stock_betas,
            "Number of Stocks": len(self.portfolio_stocks)
        }
    
    def simple_analysis(self):
        beta_analysis = self.portfolio_beta()
        if beta_analysis is None:
            return None

        portfolio_beta = beta_analysis["Portfolio Beta"]

        # risk classification
        if porfolio_beta < 1:
            risk_level = 'Low'
        elif portfolio_beta == 1:
            risk_level = 'Market Level'
        elif portfolio_beta > 1:
            risk_level = 'High'

        print(f"Portfolio Beta: {portfolio_beta:.2f} ({risk_level} Risk)")

        

