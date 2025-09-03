"""
Interactive Portfolio Input Interface

This module provides an easy-to-use interface for inputting portfolio holdings
and running beta analysis.
"""

import pandas as pd
from portfolio_beta_calculator import PortfolioBetaCalculator
import json
import os

class PortfolioInputInterface:
    """
    Interactive interface for portfolio input and management.
    """
    
    def __init__(self):
        self.calculator = PortfolioBetaCalculator()
        self.portfolio_file = "portfolio_holdings.json"
    
    def load_existing_portfolio(self) -> bool:
        """
        Load existing portfolio from JSON file.
        
        Returns:
            bool: True if portfolio loaded successfully, False otherwise
        """
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    holdings_data = json.load(f)
                
                print(f"Found existing portfolio with {len(holdings_data)} holdings:")
                for ticker, data in holdings_data.items():
                    print(f"  • {ticker}: {data['shares']} shares @ ${data['price_per_share']:.2f}")
                
                # Load into calculator
                for ticker, data in holdings_data.items():
                    self.calculator.add_portfolio_holding(
                        ticker, 
                        data['shares'], 
                        data['price_per_share']
                    )
                
                return True
            except Exception as e:
                print(f"Error loading portfolio: {e}")
                return False
        return False
    
    def save_portfolio(self):
        """
        Save current portfolio to JSON file.
        """
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.calculator.portfolio_holdings, f, indent=2)
            print(f"✓ Portfolio saved to {self.portfolio_file}")
        except Exception as e:
            print(f"Error saving portfolio: {e}")
    
    def add_holding_interactive(self):
        """
        Interactive method to add a single holding.
        """
        print("\n" + "="*40)
        print("ADD NEW HOLDING")
        print("="*40)
        
        while True:
            ticker = input("Enter stock ticker (e.g., AAPL): ").upper().strip()
            if not ticker:
                print("Ticker cannot be empty. Please try again.")
                continue
            
            try:
                shares = float(input("Enter number of shares: "))
                if shares <= 0:
                    print("Shares must be positive. Please try again.")
                    continue
            except ValueError:
                print("Invalid number. Please try again.")
                continue
            
            price_input = input("Enter current price per share (or press Enter to fetch automatically): ").strip()
            price_per_share = None
            if price_input:
                try:
                    price_per_share = float(price_input)
                    if price_per_share <= 0:
                        print("Price must be positive. Please try again.")
                        continue
                except ValueError:
                    print("Invalid price. Please try again.")
                    continue
            
            # Add the holding
            self.calculator.add_portfolio_holding(ticker, shares, price_per_share)
            
            # Ask if user wants to add another
            another = input("\nAdd another holding? (y/n): ").lower().strip()
            if another != 'y':
                break
    
    def edit_holding_interactive(self):
        """
        Interactive method to edit existing holdings.
        """
        if not self.calculator.portfolio_holdings:
            print("No holdings to edit. Add some holdings first.")
            return
        
        print("\n" + "="*40)
        print("EDIT HOLDINGS")
        print("="*40)
        
        # Display current holdings
        holdings_list = list(self.calculator.portfolio_holdings.keys())
        for i, ticker in enumerate(holdings_list, 1):
            holding = self.calculator.portfolio_holdings[ticker]
            print(f"{i}. {ticker}: {holding['shares']} shares @ ${holding['price_per_share']:.2f}")
        
        while True:
            try:
                choice = input(f"\nSelect holding to edit (1-{len(holdings_list)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    break
                
                index = int(choice) - 1
                if 0 <= index < len(holdings_list):
                    ticker = holdings_list[index]
                    holding = self.calculator.portfolio_holdings[ticker]
                    
                    print(f"\nEditing {ticker}:")
                    print(f"Current: {holding['shares']} shares @ ${holding['price_per_share']:.2f}")
                    
                    # Edit shares
                    new_shares = input(f"Enter new number of shares (current: {holding['shares']}): ").strip()
                    if new_shares:
                        try:
                            new_shares = float(new_shares)
                            if new_shares > 0:
                                holding['shares'] = new_shares
                                holding['market_value'] = new_shares * holding['price_per_share']
                                print(f"✓ Updated shares to {new_shares}")
                        except ValueError:
                            print("Invalid number. Shares not updated.")
                    
                    # Edit price
                    new_price = input(f"Enter new price per share (current: ${holding['price_per_share']:.2f}): ").strip()
                    if new_price:
                        try:
                            new_price = float(new_price)
                            if new_price > 0:
                                holding['price_per_share'] = new_price
                                holding['market_value'] = holding['shares'] * new_price
                                print(f"✓ Updated price to ${new_price:.2f}")
                        except ValueError:
                            print("Invalid price. Price not updated.")
                    
                    # Ask if user wants to edit another
                    another = input("\nEdit another holding? (y/n): ").lower().strip()
                    if another != 'y':
                        break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please try again.")
    
    def remove_holding_interactive(self):
        """
        Interactive method to remove holdings.
        """
        if not self.calculator.portfolio_holdings:
            print("No holdings to remove. Add some holdings first.")
            return
        
        print("\n" + "="*40)
        print("REMOVE HOLDINGS")
        print("="*40)
        
        # Display current holdings
        holdings_list = list(self.calculator.portfolio_holdings.keys())
        for i, ticker in enumerate(holdings_list, 1):
            holding = self.calculator.portfolio_holdings[ticker]
            print(f"{i}. {ticker}: {holding['shares']} shares @ ${holding['price_per_share']:.2f}")
        
        while True:
            try:
                choice = input(f"\nSelect holding to remove (1-{len(holdings_list)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    break
                
                index = int(choice) - 1
                if 0 <= index < len(holdings_list):
                    ticker = holdings_list[index]
                    holding = self.calculator.portfolio_holdings[ticker]
                    
                    confirm = input(f"Remove {ticker} ({holding['shares']} shares)? (y/n): ").lower().strip()
                    if confirm == 'y':
                        del self.calculator.portfolio_holdings[ticker]
                        if ticker in self.calculator.stock_data:
                            del self.calculator.stock_data[ticker]
                        print(f"✓ Removed {ticker}")
                        
                        # Update holdings list
                        holdings_list = list(self.calculator.portfolio_holdings.keys())
                        if not holdings_list:
                            print("Portfolio is now empty.")
                            break
                    
                    # Ask if user wants to remove another
                    another = input("\nRemove another holding? (y/n): ").lower().strip()
                    if another != 'y':
                        break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please try again.")
    
    def display_portfolio_summary(self):
        """
        Display a summary of current portfolio holdings.
        """
        if not self.calculator.portfolio_holdings:
            print("Portfolio is empty.")
            return
        
        print("\n" + "="*50)
        print("PORTFOLIO SUMMARY")
        print("="*50)
        
        total_value = sum(holding['market_value'] for holding in self.calculator.portfolio_holdings.values())
        
        print(f"Total Portfolio Value: ${total_value:,.2f}")
        print(f"Number of Holdings: {len(self.calculator.portfolio_holdings)}")
        print("\nHoldings:")
        
        # Sort by market value (descending)
        sorted_holdings = sorted(
            self.calculator.portfolio_holdings.items(),
            key=lambda x: x[1]['market_value'],
            reverse=True
        )
        
        for ticker, holding in sorted_holdings:
            weight = (holding['market_value'] / total_value) * 100
            print(f"  • {ticker}: {holding['shares']:,.0f} shares @ ${holding['price_per_share']:.2f} "
                  f"= ${holding['market_value']:,.2f} ({weight:.1f}%)")
    
    def run_analysis(self):
        """
        Run the complete portfolio beta analysis.
        """
        if not self.calculator.portfolio_holdings:
            print("Cannot run analysis: Portfolio is empty.")
            return
        
        print("\n" + "="*50)
        print("RUNNING PORTFOLIO BETA ANALYSIS")
        print("="*50)
        
        # Fetch benchmark data
        print("Fetching S&P 500 benchmark data...")
        self.calculator.fetch_benchmark_data()
        
        # Generate and display report
        print("\nGenerating analysis report...")
        report = self.calculator.generate_report()
        print(report)
        
        # Create visualization
        print("\nGenerating visualization...")
        self.calculator.plot_beta_analysis("portfolio_beta_analysis.png")
        
        # Save portfolio
        self.save_portfolio()
    
    def main_menu(self):
        """
        Main interactive menu for the portfolio interface.
        """
        print("Portfolio Beta Calculator")
        print("="*30)
        
        # Try to load existing portfolio
        if self.load_existing_portfolio():
            load_choice = input("\nUse existing portfolio? (y/n): ").lower().strip()
            if load_choice != 'y':
                self.calculator.portfolio_holdings = {}
                self.calculator.stock_data = {}
        
        while True:
            print("\n" + "="*30)
            print("MAIN MENU")
            print("="*30)
            print("1. View Portfolio Summary")
            print("2. Add New Holding")
            print("3. Edit Existing Holdings")
            print("4. Remove Holdings")
            print("5. Run Beta Analysis")
            print("6. Save Portfolio")
            print("7. Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == '1':
                self.display_portfolio_summary()
            elif choice == '2':
                self.add_holding_interactive()
            elif choice == '3':
                self.edit_holding_interactive()
            elif choice == '4':
                self.remove_holding_interactive()
            elif choice == '5':
                self.run_analysis()
            elif choice == '6':
                self.save_portfolio()
            elif choice == '7':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-7.")

def main():
    """
    Main function to run the interactive portfolio interface.
    """
    interface = PortfolioInputInterface()
    interface.main_menu()

if __name__ == "__main__":
    main()

