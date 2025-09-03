"""
Portfolio Beta Optimization Calculator

This module provides functionality to calculate portfolio beta compared to S&P 500,
analyze individual stock betas, and provide optimization recommendations.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PortfolioBetaCalculator:
    """
    A comprehensive portfolio beta calculator that compares portfolio performance
    against the S&P 500 benchmark.
    """
    
    def __init__(self, benchmark_ticker: str = "^GSPC"):
        """
        Initialize the calculator with a benchmark (default: S&P 500).
        
        Args:
            benchmark_ticker (str): Ticker symbol for the benchmark index
        """
        self.benchmark_ticker = benchmark_ticker
        self.benchmark_data = None
        self.stock_data = {}
        self.portfolio_holdings = {}
        
    def fetch_benchmark_data(self, period: str = "2y") -> pd.DataFrame:
        """
        Fetch benchmark data (S&P 500 by default).
        
        Args:
            period (str): Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            pd.DataFrame: Benchmark price data
        """
        try:
            benchmark = yf.Ticker(self.benchmark_ticker)
            self.benchmark_data = benchmark.history(period=period)
            print(f"✓ Fetched {len(self.benchmark_data)} days of {self.benchmark_ticker} data")
            return self.benchmark_data
        except Exception as e:
            print(f"Error fetching benchmark data: {e}")
            return None
    
    def fetch_stock_data(self, ticker: str, period: str = "2y") -> pd.DataFrame:
        """
        Fetch historical data for a specific stock.
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period for data
            
        Returns:
            pd.DataFrame: Stock price data
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            self.stock_data[ticker] = data
            print(f"✓ Fetched {len(data)} days of {ticker} data")
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def add_portfolio_holding(self, ticker: str, shares: float, price_per_share: Optional[float] = None):
        """
        Add a stock holding to the portfolio.
        
        Args:
            ticker (str): Stock ticker symbol
            shares (float): Number of shares held
            price_per_share (float, optional): Current price per share (fetched if not provided)
        """
        if price_per_share is None:
            try:
                stock = yf.Ticker(ticker)
                current_data = stock.history(period="1d")
                if current_data.empty:
                    raise ValueError(f"No data found for ticker {ticker}")
                current_price = current_data['Close'].iloc[-1]
                price_per_share = current_price
            except Exception as e:
                error_msg = f"Could not fetch current price for {ticker}: {str(e)}"
                print(f"Warning: {error_msg}")
                # Don't add to portfolio if we can't get price data
                raise ValueError(error_msg)
        
        self.portfolio_holdings[ticker] = {
            'shares': shares,
            'price_per_share': price_per_share,
            'market_value': shares * price_per_share
        }
        
        # Fetch historical data for beta calculation
        self.fetch_stock_data(ticker)
        print(f"✓ Added {shares} shares of {ticker} at ${price_per_share:.2f} per share")
    
    def calculate_individual_beta(self, ticker: str) -> float:
        """
        Calculate beta for an individual stock against the benchmark.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            float: Beta value
        """
        if ticker not in self.stock_data or self.benchmark_data is None:
            print(f"Error: Missing data for {ticker} or benchmark")
            return None
        
        # Get common date range
        stock_data = self.stock_data[ticker]
        common_dates = stock_data.index.intersection(self.benchmark_data.index)
        
        if len(common_dates) < 30:  # Need at least 30 days for reliable beta
            print(f"Warning: Insufficient data overlap for {ticker}")
            return None
        
        # Calculate daily returns
        stock_returns = stock_data.loc[common_dates, 'Close'].pct_change().dropna()
        benchmark_returns = self.benchmark_data.loc[common_dates, 'Close'].pct_change().dropna()
        
        # Align the returns
        aligned_returns = pd.DataFrame({
            'stock': stock_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned_returns) < 30:
            print(f"Warning: Insufficient aligned data for {ticker}")
            return None
        
        # Calculate beta using covariance and variance
        covariance = np.cov(aligned_returns['stock'], aligned_returns['benchmark'])[0, 1]
        benchmark_variance = np.var(aligned_returns['benchmark'])
        
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
        return beta
    
    def calculate_portfolio_beta(self) -> Dict:
        """
        Calculate the weighted average beta of the entire portfolio.
        
        Returns:
            Dict: Portfolio beta analysis results
        """
        if not self.portfolio_holdings:
            print("Error: No portfolio holdings defined")
            return None
        
        # Calculate total portfolio value
        total_value = sum(holding['market_value'] for holding in self.portfolio_holdings.values())
        
        if total_value == 0:
            print("Error: Total portfolio value is zero")
            return None
        
        # Calculate individual betas and weights
        stock_betas = {}
        weighted_betas = []
        
        for ticker, holding in self.portfolio_holdings.items():
            beta = self.calculate_individual_beta(ticker)
            if beta is not None:
                weight = holding['market_value'] / total_value
                stock_betas[ticker] = {
                    'beta': beta,
                    'weight': weight,
                    'market_value': holding['market_value'],
                    'shares': holding['shares']
                }
                weighted_betas.append(beta * weight)
        
        portfolio_beta = sum(weighted_betas)
        
        return {
            'portfolio_beta': portfolio_beta,
            'total_portfolio_value': total_value,
            'stock_betas': stock_betas,
            'num_stocks': len(stock_betas)
        }
    
    def analyze_portfolio_risk(self) -> Dict:
        """
        Analyze portfolio risk characteristics and provide insights.
        
        Returns:
            Dict: Risk analysis results
        """
        beta_analysis = self.calculate_portfolio_beta()
        if not beta_analysis:
            return None
        
        portfolio_beta = beta_analysis['portfolio_beta']
        
        # Risk classification
        if portfolio_beta < 0.8:
            risk_level = "Conservative"
            risk_description = "Lower volatility than market"
        elif portfolio_beta <= 1.2:
            risk_level = "Moderate"
            risk_description = "Similar volatility to market"
        else:
            risk_level = "Aggressive"
            risk_description = "Higher volatility than market"
        
        # Market sensitivity analysis
        if portfolio_beta < 1.0:
            market_sensitivity = f"For every 1% market move, portfolio moves {portfolio_beta:.2f}%"
        else:
            market_sensitivity = f"For every 1% market move, portfolio moves {portfolio_beta:.2f}%"
        
        return {
            'portfolio_beta': portfolio_beta,
            'risk_level': risk_level,
            'risk_description': risk_description,
            'market_sensitivity': market_sensitivity,
            'beta_analysis': beta_analysis
        }
    
    def plot_beta_analysis(self, save_path: Optional[str] = None):
        """
        Create comprehensive beta analysis visualization.
        
        Args:
            save_path (str, optional): Path to save the plot
        """
        beta_analysis = self.calculate_portfolio_beta()
        if not beta_analysis:
            print("Error: Cannot create plot without portfolio data")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Portfolio Beta Analysis', fontsize=16, fontweight='bold')
        
        # 1. Individual Stock Betas
        stock_betas = beta_analysis['stock_betas']
        tickers = list(stock_betas.keys())
        betas = [stock_betas[ticker]['beta'] for ticker in tickers]
        weights = [stock_betas[ticker]['weight'] * 100 for ticker in tickers]
        
        bars = ax1.bar(tickers, betas, color='skyblue', alpha=0.7)
        ax1.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Market Beta (1.0)')
        ax1.set_title('Individual Stock Betas')
        ax1.set_ylabel('Beta')
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)
        
        # Add weight annotations
        for bar, weight in zip(bars, weights):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{weight:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 2. Portfolio Weight Distribution
        ax2.pie(weights, labels=tickers, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Portfolio Weight Distribution')
        
        # 3. Beta vs Weight Scatter
        ax3.scatter(weights, betas, s=100, alpha=0.7, c='green')
        for i, ticker in enumerate(tickers):
            ax3.annotate(ticker, (weights[i], betas[i]), xytext=(5, 5), 
                        textcoords='offset points', fontsize=8)
        ax3.axhline(y=1.0, color='red', linestyle='--', alpha=0.7)
        ax3.set_xlabel('Portfolio Weight (%)')
        ax3.set_ylabel('Beta')
        ax3.set_title('Beta vs Portfolio Weight')
        ax3.grid(True, alpha=0.3)
        
        # 4. Portfolio Beta Summary
        portfolio_beta = beta_analysis['portfolio_beta']
        ax4.text(0.5, 0.7, f'Portfolio Beta: {portfolio_beta:.3f}', 
                ha='center', va='center', fontsize=20, fontweight='bold',
                transform=ax4.transAxes)
        
        if portfolio_beta < 0.8:
            risk_color = 'green'
            risk_text = 'Conservative Portfolio'
        elif portfolio_beta <= 1.2:
            risk_color = 'orange'
            risk_text = 'Moderate Portfolio'
        else:
            risk_color = 'red'
            risk_text = 'Aggressive Portfolio'
        
        ax4.text(0.5, 0.5, risk_text, ha='center', va='center', 
                fontsize=16, color=risk_color, transform=ax4.transAxes)
        
        ax4.text(0.5, 0.3, f'Total Value: ${beta_analysis["total_portfolio_value"]:,.2f}', 
                ha='center', va='center', fontsize=12, transform=ax4.transAxes)
        
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved to {save_path}")
        
        plt.show()
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive text report of the portfolio beta analysis.
        
        Returns:
            str: Formatted report
        """
        risk_analysis = self.analyze_portfolio_risk()
        if not risk_analysis:
            return "Error: Cannot generate report without portfolio data"
        
        beta_analysis = risk_analysis['beta_analysis']
        
        report = f"""
{'='*60}
PORTFOLIO BETA ANALYSIS REPORT
{'='*60}

PORTFOLIO SUMMARY:
• Total Portfolio Value: ${beta_analysis['total_portfolio_value']:,.2f}
• Number of Holdings: {beta_analysis['num_stocks']}
• Portfolio Beta: {risk_analysis['portfolio_beta']:.3f}
• Risk Level: {risk_analysis['risk_level']}
• Risk Description: {risk_analysis['risk_description']}

MARKET SENSITIVITY:
• {risk_analysis['market_sensitivity']}

INDIVIDUAL STOCK ANALYSIS:
"""
        
        for ticker, data in beta_analysis['stock_betas'].items():
            report += f"""
{ticker}:
  • Beta: {data['beta']:.3f}
  • Portfolio Weight: {data['weight']*100:.2f}%
  • Market Value: ${data['market_value']:,.2f}
  • Shares Held: {data['shares']:,.0f}
"""
        
        report += f"""
{'='*60}
RECOMMENDATIONS:
{'='*60}
"""
        
        portfolio_beta = risk_analysis['portfolio_beta']
        
        if portfolio_beta < 0.8:
            report += """
• Your portfolio is CONSERVATIVE with lower volatility than the market
• Consider adding some growth stocks if you want higher returns
• Good for risk-averse investors or those nearing retirement
"""
        elif portfolio_beta <= 1.2:
            report += """
• Your portfolio has MODERATE risk with market-like volatility
• Well-balanced for most investors
• Consider rebalancing if individual stock weights become too concentrated
"""
        else:
            report += """
• Your portfolio is AGGRESSIVE with higher volatility than the market
• Higher potential returns but also higher risk
• Consider adding defensive stocks or bonds to reduce volatility
"""
        
        # High beta stock warnings
        high_beta_stocks = [ticker for ticker, data in beta_analysis['stock_betas'].items() 
                           if data['beta'] > 1.5]
        if high_beta_stocks:
            report += f"""
• HIGH BETA WARNING: {', '.join(high_beta_stocks)} have betas > 1.5
  These stocks will amplify market movements significantly
"""
        
        # Concentration risk
        max_weight = max(data['weight'] for data in beta_analysis['stock_betas'].values())
        if max_weight > 0.3:
            report += f"""
• CONCENTRATION WARNING: Your largest holding represents {max_weight*100:.1f}% of portfolio
  Consider diversifying to reduce concentration risk
"""
        
        return report

def main():
    """
    Example usage of the PortfolioBetaCalculator.
    """
    print("Portfolio Beta Calculator - Example Usage")
    print("="*50)
    
    # Initialize calculator
    calculator = PortfolioBetaCalculator()
    
    # Fetch benchmark data
    calculator.fetch_benchmark_data()
    
    # Example portfolio (you can modify these)
    example_holdings = {
        'AAPL': 10,    # 10 shares of Apple
        'MSFT': 5,     # 5 shares of Microsoft
        'GOOGL': 2,    # 2 shares of Google
        'TSLA': 3,     # 3 shares of Tesla
        'JNJ': 8,      # 8 shares of Johnson & Johnson
    }
    
    print("\nAdding example portfolio holdings...")
    for ticker, shares in example_holdings.items():
        calculator.add_portfolio_holding(ticker, shares)
    
    # Calculate and display results
    print("\n" + "="*50)
    print("CALCULATING PORTFOLIO BETA...")
    print("="*50)
    
    # Generate report
    report = calculator.generate_report()
    print(report)
    
    # Create visualization
    print("\nGenerating beta analysis plot...")
    calculator.plot_beta_analysis()
    
    return calculator

if __name__ == "__main__":
    calculator = main()
