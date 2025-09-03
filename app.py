"""
Flask Web Application for Portfolio Beta Calculator

A web-based interface for the portfolio beta optimization tool.
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from portfolio_beta_calculator import PortfolioBetaCalculator
from watchlist_integration import WatchlistBetaOptimizer
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

app = Flask(__name__)

# Global instances
calculator = PortfolioBetaCalculator()
watchlist_optimizer = WatchlistBetaOptimizer()

@app.route('/')
def index():
    """Main page with portfolio input form."""
    return render_template('index.html')

@app.route('/add_holding', methods=['POST'])
def add_holding():
    """Add a new holding to the portfolio."""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        shares = float(data.get('shares', 0))
        price = data.get('price', None)
        
        if not ticker or shares <= 0:
            return jsonify({'success': False, 'error': 'Invalid ticker or shares'})
        
        if price:
            price = float(price)
        
        # Validate ticker exists before adding
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            # Try to get current price to validate ticker
            current_data = stock.history(period="1d")
            if current_data.empty:
                return jsonify({
                    'success': False, 
                    'error': f'Ticker "{ticker}" not found. Please check the symbol and try again. Common issues: GOOGLE should be GOOGL, FACEBOOK should be META, etc.'
                })
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'Error validating ticker "{ticker}": {str(e)}. Please check the symbol and try again.'
            })
        
        calculator.add_portfolio_holding(ticker, shares, price)
        
        return jsonify({
            'success': True, 
            'message': f'Added {shares} shares of {ticker}',
            'portfolio': calculator.portfolio_holdings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_holding', methods=['POST'])
def remove_holding():
    """Remove a holding from the portfolio."""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        
        if ticker in calculator.portfolio_holdings:
            del calculator.portfolio_holdings[ticker]
            if ticker in calculator.stock_data:
                del calculator.stock_data[ticker]
            return jsonify({'success': True, 'message': f'Removed {ticker}'})
        else:
            return jsonify({'success': False, 'error': f'{ticker} not found in portfolio'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_portfolio')
def get_portfolio():
    """Get current portfolio holdings."""
    return jsonify(calculator.portfolio_holdings)

@app.route('/analyze', methods=['POST'])
def analyze_portfolio():
    """Run portfolio beta analysis."""
    try:
        if not calculator.portfolio_holdings:
            return jsonify({'success': False, 'error': 'Portfolio is empty'})
        
        # Fetch benchmark data
        calculator.fetch_benchmark_data()
        
        # Calculate portfolio beta
        beta_analysis = calculator.calculate_portfolio_beta()
        if not beta_analysis:
            return jsonify({'success': False, 'error': 'Failed to calculate portfolio beta'})
        
        # Get risk analysis
        risk_analysis = calculator.analyze_portfolio_risk()
        
        # Create visualization
        chart_data = create_chart_data(beta_analysis)
        
        return jsonify({
            'success': True,
            'beta_analysis': beta_analysis,
            'risk_analysis': risk_analysis,
            'chart_data': chart_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_portfolio', methods=['POST'])
def clear_portfolio():
    """Clear all portfolio holdings."""
    try:
        calculator.portfolio_holdings = {}
        calculator.stock_data = {}
        return jsonify({'success': True, 'message': 'Portfolio cleared'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_portfolio', methods=['POST'])
def save_portfolio():
    """Save portfolio to file."""
    try:
        with open('portfolio_holdings.json', 'w') as f:
            json.dump(calculator.portfolio_holdings, f, indent=2)
        return jsonify({'success': True, 'message': 'Portfolio saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/load_portfolio', methods=['POST'])
def load_portfolio():
    """Load portfolio from file."""
    try:
        if os.path.exists('portfolio_holdings.json'):
            with open('portfolio_holdings.json', 'r') as f:
                holdings = json.load(f)
            
            # Clear current portfolio
            calculator.portfolio_holdings = {}
            calculator.stock_data = {}
            
            # Load holdings
            for ticker, data in holdings.items():
                calculator.add_portfolio_holding(
                    ticker, 
                    data['shares'], 
                    data['price_per_share']
                )
            
            return jsonify({'success': True, 'message': 'Portfolio loaded', 'portfolio': holdings})
        else:
            return jsonify({'success': False, 'error': 'No saved portfolio found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Watchlist API endpoints
@app.route('/get_watchlist')
def get_watchlist():
    """Get current watchlist with beta data."""
    try:
        watchlist_data = watchlist_optimizer.get_watchlist_with_betas()
        return jsonify({'success': True, 'watchlist': watchlist_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    """Add a stock to the watchlist."""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        
        if not ticker:
            return jsonify({'success': False, 'error': 'Invalid ticker'})
        
        success = watchlist_optimizer.add_to_watchlist(ticker)
        if success:
            return jsonify({'success': True, 'message': f'{ticker} added to watchlist'})
        else:
            return jsonify({'success': False, 'error': f'Could not add {ticker} to watchlist'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_from_watchlist', methods=['POST'])
def remove_from_watchlist():
    """Remove a stock from the watchlist."""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        
        success = watchlist_optimizer.remove_from_watchlist(ticker)
        if success:
            return jsonify({'success': True, 'message': f'{ticker} removed from watchlist'})
        else:
            return jsonify({'success': False, 'error': f'{ticker} not found in watchlist'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_beta_recommendations', methods=['POST'])
def get_beta_recommendations():
    """Get beta balancing recommendations from watchlist."""
    try:
        data = request.get_json()
        target_beta = data.get('target_beta', 1.0)
        
        # Calculate current portfolio beta
        beta_analysis = calculator.calculate_portfolio_beta()
        if not beta_analysis:
            return jsonify({'success': False, 'error': 'No portfolio holdings to analyze'})
        
        current_beta = beta_analysis['portfolio_beta']
        
        # Get recommendations
        recommendations = watchlist_optimizer.get_beta_balancing_recommendations(
            current_beta, target_beta
        )
        
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_sector_analysis')
def get_sector_analysis():
    """Get sector analysis of watchlist."""
    try:
        sector_analysis = watchlist_optimizer.get_sector_analysis()
        return jsonify({'success': True, 'sector_analysis': sector_analysis})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_risk_diversification')
def get_risk_diversification():
    """Get risk diversification recommendations."""
    try:
        diversification = watchlist_optimizer.get_risk_diversification_recommendations()
        return jsonify({'success': True, 'diversification': diversification})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def create_chart_data(beta_analysis):
    """Create chart data for visualization."""
    stock_betas = beta_analysis['stock_betas']
    
    # Prepare data for charts
    tickers = list(stock_betas.keys())
    betas = [stock_betas[ticker]['beta'] for ticker in tickers]
    weights = [stock_betas[ticker]['weight'] * 100 for ticker in tickers]
    market_values = [stock_betas[ticker]['market_value'] for ticker in tickers]
    
    return {
        'tickers': tickers,
        'betas': betas,
        'weights': weights,
        'market_values': market_values,
        'portfolio_beta': beta_analysis['portfolio_beta'],
        'total_value': beta_analysis['total_portfolio_value']
    }

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Starting Portfolio Beta Calculator Web App...")
    print("Open your browser and go to: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)
