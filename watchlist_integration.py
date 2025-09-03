"""
Watchlist Integration for Portfolio Beta Calculator

This module integrates the existing watchlist functionality with the portfolio beta calculator
to provide intelligent beta balancing recommendations.
"""

import json
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from portfolio_beta_calculator import PortfolioBetaCalculator

class WatchlistBetaOptimizer:
    """
    Integrates watchlist functionality with portfolio beta optimization.
    """
    
    def __init__(self, watchlist_file: str = "watchlist.json"):
        self.watchlist_file = watchlist_file
        self.calculator = PortfolioBetaCalculator()
    
    def load_watchlist(self) -> List[str]:
        """
        Load watchlist from JSON file.
        
        Returns:
            List[str]: List of ticker symbols
        """
        try:
            with open(self.watchlist_file, 'r') as f:
                tickers = json.load(f)
            return tickers
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading watchlist: {e}")
            return []
    
    def save_watchlist(self, tickers: List[str]):
        """
        Save watchlist to JSON file.
        
        Args:
            tickers (List[str]): List of ticker symbols
        """
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(tickers, f, indent=2)
        except Exception as e:
            print(f"Error saving watchlist: {e}")
    
    def add_to_watchlist(self, ticker: str) -> bool:
        """
        Add a ticker to the watchlist.
        
        Args:
            ticker (str): Ticker symbol to add
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        ticker = ticker.upper().strip()
        tickers = self.load_watchlist()
        
        if ticker not in tickers:
            # Validate ticker exists
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(period='1d')
                if not data.empty:
                    tickers.append(ticker)
                    self.save_watchlist(tickers)
                    return True
                else:
                    return False
            except Exception:
                return False
        return True  # Already exists
    
    def remove_from_watchlist(self, ticker: str) -> bool:
        """
        Remove a ticker from the watchlist.
        
        Args:
            ticker (str): Ticker symbol to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        ticker = ticker.upper().strip()
        tickers = self.load_watchlist()
        
        if ticker in tickers:
            tickers.remove(ticker)
            self.save_watchlist(tickers)
            return True
        return False
    
    def get_watchlist_with_betas(self) -> List[Dict]:
        """
        Get watchlist stocks with their beta values.
        
        Returns:
            List[Dict]: List of stock data with beta information
        """
        tickers = self.load_watchlist()
        watchlist_data = []
        
        # Fetch benchmark data for beta calculation
        self.calculator.fetch_benchmark_data()
        
        for ticker in tickers:
            try:
                # Get current stock data
                stock = yf.Ticker(ticker)
                current_data = stock.history(period='1d')
                
                if not current_data.empty:
                    current_price = current_data['Close'].iloc[-1]
                    
                    # Fetch historical data for beta calculation
                    self.calculator.fetch_stock_data(ticker)
                    
                    # Calculate beta
                    beta = self.calculator.calculate_individual_beta(ticker)
                    
                    # Get additional stock info
                    info = stock.info
                    
                    stock_data = {
                        'ticker': ticker,
                        'current_price': current_price,
                        'beta': beta if beta is not None else 0,
                        'market_cap': info.get('marketCap', 0),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown'),
                        'pe_ratio': info.get('trailingPE', 0),
                        'dividend_yield': info.get('dividendYield', 0),
                        'risk_level': self._classify_risk_level(beta) if beta is not None else 'Unknown'
                    }
                    
                    watchlist_data.append(stock_data)
                    
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                continue
        
        return watchlist_data
    
    def _classify_risk_level(self, beta: float) -> str:
        """
        Classify risk level based on beta.
        
        Args:
            beta (float): Stock beta value
            
        Returns:
            str: Risk level classification
        """
        if beta < 0.8:
            return "Conservative"
        elif beta <= 1.2:
            return "Moderate"
        else:
            return "Aggressive"
    
    def get_beta_balancing_recommendations(self, current_portfolio_beta: float, 
                                         target_beta: Optional[float] = None) -> Dict:
        """
        Get recommendations for balancing portfolio beta using watchlist stocks.
        
        Args:
            current_portfolio_beta (float): Current portfolio beta
            target_beta (float, optional): Target beta (default: 1.0 for market-like)
            
        Returns:
            Dict: Recommendations for beta balancing
        """
        if target_beta is None:
            target_beta = 1.0
        
        watchlist_data = self.get_watchlist_with_betas()
        
        # Filter out stocks already in portfolio
        portfolio_tickers = set(self.calculator.portfolio_holdings.keys())
        available_stocks = [stock for stock in watchlist_data 
                           if stock['ticker'] not in portfolio_tickers]
        
        if not available_stocks:
            return {
                'message': 'No stocks available in watchlist that are not already in portfolio',
                'recommendations': []
            }
        
        # Calculate beta difference
        beta_difference = target_beta - current_portfolio_beta
        
        if abs(beta_difference) < 0.05:  # Already close to target
            return {
                'message': f'Portfolio beta ({current_portfolio_beta:.3f}) is already close to target ({target_beta:.3f})',
                'recommendations': []
            }
        
        # Sort stocks by how well they help achieve target beta
        if beta_difference > 0:  # Need to increase beta
            # Sort by beta descending (highest beta first)
            recommendations = sorted(available_stocks, key=lambda x: x['beta'], reverse=True)
            action = "increase"
        else:  # Need to decrease beta
            # Sort by beta ascending (lowest beta first)
            recommendations = sorted(available_stocks, key=lambda x: x['beta'])
            action = "decrease"
        
        # Create detailed recommendations
        detailed_recommendations = []
        for stock in recommendations[:5]:  # Top 5 recommendations
            impact = self._calculate_beta_impact(stock['beta'], current_portfolio_beta)
            
            detailed_recommendations.append({
                'ticker': stock['ticker'],
                'current_price': stock['current_price'],
                'beta': stock['beta'],
                'risk_level': stock['risk_level'],
                'sector': stock['sector'],
                'industry': stock['industry'],
                'market_cap': stock['market_cap'],
                'pe_ratio': stock['pe_ratio'],
                'dividend_yield': stock['dividend_yield'],
                'beta_impact': impact,
                'reason': self._get_recommendation_reason(stock, action, beta_difference)
            })
        
        return {
            'current_beta': current_portfolio_beta,
            'target_beta': target_beta,
            'beta_difference': beta_difference,
            'action_needed': action,
            'recommendations': detailed_recommendations,
            'message': f'To {action} portfolio beta from {current_portfolio_beta:.3f} to {target_beta:.3f}'
        }
    
    def _calculate_beta_impact(self, stock_beta: float, current_portfolio_beta: float) -> str:
        """
        Calculate the impact of adding a stock to the portfolio beta.
        
        Args:
            stock_beta (float): Individual stock beta
            current_portfolio_beta (float): Current portfolio beta
            
        Returns:
            str: Description of beta impact
        """
        if stock_beta > current_portfolio_beta:
            return "Will increase portfolio beta"
        elif stock_beta < current_portfolio_beta:
            return "Will decrease portfolio beta"
        else:
            return "Will maintain portfolio beta"
    
    def _get_recommendation_reason(self, stock: Dict, action: str, beta_difference: float) -> str:
        """
        Get a human-readable reason for the recommendation.
        
        Args:
            stock (Dict): Stock data
            action (str): Action needed (increase/decrease)
            beta_difference (float): Difference between current and target beta
            
        Returns:
            str: Recommendation reason
        """
        beta = stock['beta']
        ticker = stock['ticker']
        
        if action == "increase":
            if beta > 1.5:
                return f"{ticker} has high beta ({beta:.2f}) - excellent for increasing portfolio volatility"
            elif beta > 1.2:
                return f"{ticker} has moderate-high beta ({beta:.2f}) - good for increasing portfolio volatility"
            else:
                return f"{ticker} has moderate beta ({beta:.2f}) - will help increase portfolio volatility"
        else:  # decrease
            if beta < 0.8:
                return f"{ticker} has low beta ({beta:.2f}) - excellent for reducing portfolio volatility"
            elif beta < 1.0:
                return f"{ticker} has moderate-low beta ({beta:.2f}) - good for reducing portfolio volatility"
            else:
                return f"{ticker} has moderate beta ({beta:.2f}) - will help reduce portfolio volatility"
    
    def get_sector_analysis(self) -> Dict:
        """
        Analyze watchlist by sectors and their beta characteristics.
        
        Returns:
            Dict: Sector analysis with average betas
        """
        watchlist_data = self.get_watchlist_with_betas()
        
        sector_analysis = {}
        for stock in watchlist_data:
            sector = stock['sector']
            if sector not in sector_analysis:
                sector_analysis[sector] = {
                    'stocks': [],
                    'avg_beta': 0,
                    'count': 0,
                    'total_beta': 0
                }
            
            sector_analysis[sector]['stocks'].append(stock)
            sector_analysis[sector]['total_beta'] += stock['beta']
            sector_analysis[sector]['count'] += 1
        
        # Calculate average betas
        for sector, data in sector_analysis.items():
            if data['count'] > 0:
                data['avg_beta'] = data['total_beta'] / data['count']
                data['risk_level'] = self._classify_risk_level(data['avg_beta'])
        
        return sector_analysis
    
    def get_risk_diversification_recommendations(self) -> Dict:
        """
        Get recommendations for risk diversification across the watchlist.
        
        Returns:
            Dict: Risk diversification recommendations
        """
        watchlist_data = self.get_watchlist_with_betas()
        
        if not watchlist_data:
            return {'message': 'No stocks in watchlist', 'recommendations': []}
        
        # Categorize stocks by risk level
        conservative_stocks = [s for s in watchlist_data if s['beta'] < 0.8]
        moderate_stocks = [s for s in watchlist_data if 0.8 <= s['beta'] <= 1.2]
        aggressive_stocks = [s for s in watchlist_data if s['beta'] > 1.2]
        
        recommendations = []
        
        # Check for diversification opportunities
        if len(conservative_stocks) == 0:
            recommendations.append({
                'type': 'Add Conservative Stocks',
                'message': 'Consider adding low-beta stocks for stability',
                'suggestions': [s for s in watchlist_data if s['beta'] < 1.0][:3]
            })
        
        if len(aggressive_stocks) == 0:
            recommendations.append({
                'type': 'Add Growth Stocks',
                'message': 'Consider adding high-beta stocks for growth potential',
                'suggestions': [s for s in watchlist_data if s['beta'] > 1.2][:3]
            })
        
        return {
            'conservative_count': len(conservative_stocks),
            'moderate_count': len(moderate_stocks),
            'aggressive_count': len(aggressive_stocks),
            'total_stocks': len(watchlist_data),
            'recommendations': recommendations
        }

def main():
    """
    Example usage of the WatchlistBetaOptimizer.
    """
    print("Watchlist Beta Optimizer - Example Usage")
    print("=" * 50)
    
    optimizer = WatchlistBetaOptimizer()
    
    # Load current watchlist
    watchlist = optimizer.load_watchlist()
    print(f"Current watchlist: {watchlist}")
    
    # Get watchlist with beta data
    print("\nFetching watchlist with beta data...")
    watchlist_data = optimizer.get_watchlist_with_betas()
    
    for stock in watchlist_data:
        print(f"{stock['ticker']}: Beta = {stock['beta']:.3f}, Risk = {stock['risk_level']}, "
              f"Sector = {stock['sector']}")
    
    # Example beta balancing recommendations
    print("\nBeta Balancing Recommendations:")
    print("-" * 30)
    
    # Simulate current portfolio beta
    current_beta = 1.1
    recommendations = optimizer.get_beta_balancing_recommendations(current_beta, target_beta=1.0)
    
    print(f"Current Portfolio Beta: {recommendations['current_beta']:.3f}")
    print(f"Target Beta: {recommendations['target_beta']:.3f}")
    print(f"Action Needed: {recommendations['action_needed']}")
    print(f"Message: {recommendations['message']}")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(recommendations['recommendations'][:3], 1):
        print(f"{i}. {rec['ticker']} (Beta: {rec['beta']:.3f}) - {rec['reason']}")
    
    # Sector analysis
    print("\nSector Analysis:")
    print("-" * 20)
    sector_analysis = optimizer.get_sector_analysis()
    
    for sector, data in sector_analysis.items():
        print(f"{sector}: {data['count']} stocks, Avg Beta: {data['avg_beta']:.3f}, "
              f"Risk: {data['risk_level']}")

if __name__ == "__main__":
    main()
