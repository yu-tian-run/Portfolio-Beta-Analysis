# Portfolio Beta Optimization Calculator

A comprehensive Python tool for calculating and analyzing portfolio beta compared to the S&P 500 benchmark. This tool helps you understand your portfolio's risk characteristics and market sensitivity.

## Features

- **Portfolio Beta Calculation**: Calculate weighted average beta of your entire portfolio
- **Individual Stock Analysis**: Analyze beta for each stock in your portfolio
- **Risk Assessment**: Classify portfolio as Conservative, Moderate, or Aggressive
- **Interactive Interface**: Easy-to-use menu system for portfolio management
- **Data Visualization**: Comprehensive charts and graphs for analysis
- **Portfolio Management**: Save, load, and edit portfolio holdings
- **Real-time Data**: Fetch current stock prices and historical data from Yahoo Finance

## Installation

1. **Clone or download** this repository to your local machine

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python portfolio_input_interface.py
   ```

## Quick Start

### Method 1: Interactive Interface (Recommended)
```bash
python portfolio_input_interface.py
```
This will launch an interactive menu where you can:
- Add your stock holdings
- Edit existing positions
- Run beta analysis
- Save your portfolio

### Method 2: Direct Usage
```python
from portfolio_beta_calculator import PortfolioBetaCalculator

# Initialize calculator
calculator = PortfolioBetaCalculator()

# Fetch benchmark data (S&P 500)
calculator.fetch_benchmark_data()

# Add your holdings
calculator.add_portfolio_holding('AAPL', 10)  # 10 shares of Apple
calculator.add_portfolio_holding('MSFT', 5)   # 5 shares of Microsoft
calculator.add_portfolio_holding('GOOGL', 2)  # 2 shares of Google

# Run analysis
report = calculator.generate_report()
print(report)

# Create visualization
calculator.plot_beta_analysis()
```

## Understanding Beta

**Beta** measures how much a stock or portfolio moves relative to the market (S&P 500):

- **Beta = 1.0**: Moves exactly with the market
- **Beta > 1.0**: More volatile than the market (amplifies market movements)
- **Beta < 1.0**: Less volatile than the market (dampens market movements)

### Risk Classifications:
- **Conservative (Beta < 0.8)**: Lower volatility, good for risk-averse investors
- **Moderate (Beta 0.8-1.2)**: Market-like volatility, balanced approach
- **Aggressive (Beta > 1.2)**: Higher volatility, higher potential returns/risk

## Portfolio Input Methods

### 1. Interactive Menu
The easiest way to input your portfolio:
- Run `python portfolio_input_interface.py`
- Follow the menu prompts to add/edit holdings
- Portfolio is automatically saved to `portfolio_holdings.json`

### 2. Programmatic Input
```python
# Add holdings with current market prices
calculator.add_portfolio_holding('AAPL', 10)  # Fetches current price automatically

# Add holdings with specific prices
calculator.add_portfolio_holding('AAPL', 10, 150.00)  # 10 shares at $150 each
```

### 3. Batch Input
```python
holdings = {
    'AAPL': 10,
    'MSFT': 5,
    'GOOGL': 2,
    'TSLA': 3,
    'JNJ': 8
}

for ticker, shares in holdings.items():
    calculator.add_portfolio_holding(ticker, shares)
```

## Output and Analysis

The tool provides:

1. **Text Report**: Comprehensive analysis including:
   - Portfolio beta and risk classification
   - Individual stock betas and weights
   - Market sensitivity analysis
   - Risk recommendations

2. **Visual Charts**: Four-panel visualization showing:
   - Individual stock betas
   - Portfolio weight distribution
   - Beta vs weight scatter plot
   - Portfolio summary

3. **Saved Files**:
   - `portfolio_holdings.json`: Your portfolio data
   - `portfolio_beta_analysis.png`: Analysis charts

## Example Output

```
============================================================
PORTFOLIO BETA ANALYSIS REPORT
============================================================

PORTFOLIO SUMMARY:
• Total Portfolio Value: $25,450.00
• Number of Holdings: 5
• Portfolio Beta: 1.156
• Risk Level: Moderate
• Risk Description: Similar volatility to market

MARKET SENSITIVITY:
• For every 1% market move, portfolio moves 1.16%

INDIVIDUAL STOCK ANALYSIS:

AAPL:
  • Beta: 1.234
  • Portfolio Weight: 35.2%
  • Market Value: $8,950.00
  • Shares Held: 10

MSFT:
  • Beta: 0.987
  • Portfolio Weight: 28.1%
  • Market Value: $7,150.00
  • Shares Held: 5
```

## File Structure

```
Portfolio Beta Optimization/
├── portfolio_beta_calculator.py    # Main calculation engine
├── portfolio_input_interface.py    # Interactive interface
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── portfolio_holdings.json        # Your saved portfolio (created after first use)
└── portfolio_beta_analysis.png    # Analysis charts (created after analysis)
```

## Troubleshooting

### Common Issues:

1. **"Error fetching data"**: Check your internet connection and ticker symbols
2. **"Insufficient data"**: Some stocks may not have enough historical data
3. **Import errors**: Make sure all requirements are installed: `pip install -r requirements.txt`

### Data Requirements:
- Minimum 30 days of overlapping data between stock and S&P 500
- Valid ticker symbols (use Yahoo Finance format)
- Internet connection for real-time data fetching

## Advanced Usage

### Custom Benchmark
```python
# Use a different benchmark (e.g., NASDAQ)
calculator = PortfolioBetaCalculator(benchmark_ticker="^IXIC")
```

### Custom Time Period
```python
# Use 1 year of data instead of default 2 years
calculator.fetch_benchmark_data(period="1y")
calculator.fetch_stock_data('AAPL', period="1y")
```

### Batch Analysis
```python
# Analyze multiple portfolios
portfolios = ['tech_portfolio.json', 'diversified_portfolio.json']
for portfolio_file in portfolios:
    # Load and analyze each portfolio
    pass
```

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## Disclaimer

This tool is for educational and informational purposes only. It should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions.

