"""
Example Usage of Portfolio Beta Calculator

This script demonstrates how to use the portfolio beta calculator
with a sample portfolio.
"""

from portfolio_beta_calculator import PortfolioBetaCalculator

def example_portfolio_analysis():
    """
    Example of analyzing a sample portfolio.
    """
    print("Portfolio Beta Calculator - Example Analysis")
    print("=" * 50)
    
    # Initialize the calculator
    calculator = PortfolioBetaCalculator()
    
    # Fetch S&P 500 benchmark data
    print("Fetching S&P 500 benchmark data...")
    calculator.fetch_benchmark_data(period="2y")
    
    # Define a sample portfolio
    sample_portfolio = {
        'AAPL': 15,    # Apple - Technology
        'MSFT': 10,    # Microsoft - Technology  
        'JNJ': 20,     # Johnson & Johnson - Healthcare
        'JPM': 8,      # JPMorgan Chase - Financial
        'PG': 12,      # Procter & Gamble - Consumer Staples
        'TSLA': 3,     # Tesla - Electric Vehicles
        'NVDA': 5,     # NVIDIA - Technology
        'KO': 25,      # Coca-Cola - Consumer Staples
    }
    
    print(f"\nAdding {len(sample_portfolio)} stocks to portfolio...")
    
    # Add each stock to the portfolio
    for ticker, shares in sample_portfolio.items():
        print(f"Adding {shares} shares of {ticker}...")
        calculator.add_portfolio_holding(ticker, shares)
    
    print("\n" + "=" * 50)
    print("PORTFOLIO ANALYSIS RESULTS")
    print("=" * 50)
    
    # Generate comprehensive report
    report = calculator.generate_report()
    print(report)
    
    # Create visualization
    print("\nGenerating portfolio beta visualization...")
    calculator.plot_beta_analysis("example_portfolio_analysis.png")
    
    # Additional analysis
    print("\n" + "=" * 50)
    print("ADDITIONAL INSIGHTS")
    print("=" * 50)
    
    # Get detailed beta analysis
    beta_analysis = calculator.calculate_portfolio_beta()
    if beta_analysis:
        print(f"Portfolio contains {beta_analysis['num_stocks']} stocks")
        print(f"Total portfolio value: ${beta_analysis['total_portfolio_value']:,.2f}")
        
        # Find highest and lowest beta stocks
        stock_betas = beta_analysis['stock_betas']
        if stock_betas:
            highest_beta = max(stock_betas.items(), key=lambda x: x[1]['beta'])
            lowest_beta = min(stock_betas.items(), key=lambda x: x[1]['beta'])
            
            print(f"\nHighest Beta Stock: {highest_beta[0]} (β = {highest_beta[1]['beta']:.3f})")
            print(f"Lowest Beta Stock: {lowest_beta[0]} (β = {lowest_beta[1]['beta']:.3f})")
            
            # Concentration analysis
            max_weight = max(data['weight'] for data in stock_betas.values())
            max_weight_stock = max(stock_betas.items(), key=lambda x: x[1]['weight'])
            
            print(f"\nLargest Position: {max_weight_stock[0]} ({max_weight*100:.1f}% of portfolio)")
            
            if max_weight > 0.3:
                print("⚠️  WARNING: High concentration in single stock")
            elif max_weight > 0.2:
                print("⚠️  CAUTION: Moderate concentration in single stock")
            else:
                print("✓ Portfolio is well-diversified")

def quick_beta_check():
    """
    Quick example of checking individual stock betas.
    """
    print("\n" + "=" * 50)
    print("QUICK BETA CHECK - Individual Stocks")
    print("=" * 50)
    
    calculator = PortfolioBetaCalculator()
    calculator.fetch_benchmark_data(period="1y")
    
    # Check betas for popular stocks
    stocks_to_check = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JNJ', 'JPM', 'PG']
    
    print("Individual Stock Betas (vs S&P 500):")
    print("-" * 40)
    
    for ticker in stocks_to_check:
        try:
            calculator.fetch_stock_data(ticker, period="1y")
            beta = calculator.calculate_individual_beta(ticker)
            if beta is not None:
                if beta > 1.2:
                    risk_level = "High Risk"
                elif beta < 0.8:
                    risk_level = "Low Risk"
                else:
                    risk_level = "Moderate Risk"
                
                print(f"{ticker:6}: β = {beta:5.3f} ({risk_level})")
            else:
                print(f"{ticker:6}: Unable to calculate beta")
        except Exception as e:
            print(f"{ticker:6}: Error - {e}")

if __name__ == "__main__":
    # Run the example portfolio analysis
    example_portfolio_analysis()
    
    # Run quick beta check
    quick_beta_check()
    
    print("\n" + "=" * 50)
    print("Example completed!")
    print("Check 'example_portfolio_analysis.png' for the visualization.")
    print("=" * 50)

