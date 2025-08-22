from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import google.generativeai as genai
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime, timedelta
import requests
import pandas as pd
import os
import time
import random

# Configuration
genai.configure(api_key=os.environ.get('GENAI_API_KEY'))
MARKETAUX_API_KEY = os.environ.get('MARKETAUX_API_KEY')


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache stock lists to avoid frequent API calls
stock_list_cache = {
    'last_updated': None,
    'NSE': [],
    'BSE': []
}

def fetch_nse_stocks():
    """Fetch NSE stocks from Yahoo Finance"""
    try:
        # Get Nifty 50 components as base list
        nifty_url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
        df = pd.read_csv(nifty_url)
        return [f"{symbol}.NS" for symbol in df['Symbol'].tolist()]
    except:
        # Fallback to hardcoded list if API fails
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HCLTECH.NS"]

def fetch_bse_stocks():
    """Fetch BSE stocks using Yahoo Finance search"""
    try:
        # Get BSE Sensex components
        bse_url = "https://api.bseindia.com/BseIndiaAPI/api/ListedScripData/w?scripsecid=10&scripcategory=10"
        response = requests.get(bse_url)
        data = response.json()
        return [f"{item['scrip_cd']}.BO" for item in data['Table']]
    except:
        # Fallback to hardcoded list
        return ["RELIANCE.BO", "TCS.BO", "HDFCBANK.BO", "INFY.BO", "BAFNAPH.BO"]

def refresh_stock_lists():
    """Refresh stock lists if cache is stale (>24 hours old)"""
    if not stock_list_cache['last_updated'] or \
       (datetime.now() - stock_list_cache['last_updated']).days >= 1:
        stock_list_cache['NSE'] = fetch_nse_stocks()
        stock_list_cache['BSE'] = fetch_bse_stocks()
        stock_list_cache['last_updated'] = datetime.now()

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Endpoint to fetch available stocks by exchange"""
    try:
        refresh_stock_lists()
        exchange = request.args.get('exchange', 'NSE').upper()
        
        return jsonify({
            'NSE': stock_list_cache['NSE'],
            'BSE': stock_list_cache['BSE'],
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'stocks': {
                'NSE': ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
                'BSE': ["RELIANCE.BO", "TCS.BO", "HDFCBANK.BO"]
            }
        }), 500



@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """Endpoint to analyze a stock"""
    try:
        data = request.json
        symbol = data['symbol']
        
        # Get fundamentals
        fundamentals = get_stock_fundamentals(symbol)
        if not fundamentals:
            return jsonify({'error': 'Rate limited by Yahoo Finance. Please try again in a moment.',
                'retryable': True}), 429
        
        # Get news
        news_headlines, _ = get_marketaux_news(symbol.split('.')[0])
        
        # Generate chart
        chart = generate_price_chart(symbol)
        
        # Generate analysis
        prompt = generate_analysis_prompt(fundamentals, news_headlines, [])
        analysis = analyze_with_gemini(prompt)
        
        return jsonify({
            'fundamentals': {
                'name': fundamentals.get('Name'),
                'symbol': symbol,
                'price': fundamentals.get('Current Price'),
                'pe': fundamentals.get('PE Ratio'),
                'marketCap': fundamentals.get('Market Cap'),
                'debtToEquity': fundamentals.get('Debt to Equity'),
                'priceChange': fundamentals.get('Price Change (%)')
            },
            'chart': chart,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_stock_fundamentals(stock_symbol: str) -> dict:
    """Fetch comprehensive fundamental data for a stock"""
    try:
        FMP_API_KEY = os.environ.get('FMP_API_KEY')
        
        if FMP_API_KEY:
            # Use Financial Modeling Prep
            symbol = stock_symbol.split('.')[0]  # Remove .NS/.BO
            url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                stock_data = data[0]
                return {
                    "Name": stock_data.get("companyName", symbol),
                    "Sector": stock_data.get("sector", "N/A"),
                    "Industry": stock_data.get("industry", "N/A"),
                    "Current Price": stock_data.get("price", "N/A"),
                    "Market Cap": stock_data.get("mktCap", "N/A"),
                    "PE Ratio": stock_data.get("pe", "N/A"),
                    "Price to Book": stock_data.get("pb", "N/A"),
                    "Debt to Equity": stock_data.get("debtToEquity", "N/A"),
                }
        
        # Fallback to Yahoo Finance with longer delay if FMP fails or no API key
        time.sleep(3 + random.uniform(0, 2))  # 3-5 second delay
        stock = yf.Ticker(stock_symbol)
        info = stock.info
        
        # Get historical data for trend analysis
        hist = stock.history(period="1y")
        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100 if not hist.empty else 0
        
        data = {
            "Name": info.get("shortName", stock_symbol),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Current Price": info.get("currentPrice", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "Price to Book": info.get("priceToBook", "N/A"),
            "Debt to Equity": info.get("debtToEquity", "N/A"),
            "Price Change (%)": round(price_change, 2),
        }
        
        return {k: v for k, v in data.items() if v != "N/A"}
        
    except Exception as e:
        print(f"Error fetching fundamentals: {e}")
        return {}

def get_marketaux_news(stock_symbol: str, num_results: int = 3) -> tuple:
    """Fetch recent news headlines"""
    try:
        url = f"https://api.marketaux.com/v1/news/all?symbols={stock_symbol}&filter_entities=true&language=en&api_token={MARKETAUX_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("data", [])
        headlines = [f"{article['title']} ({article['published_at'][:10]})" for article in articles[:num_results]]
        return headlines, []
    except Exception as e:
        print(f"Error fetching news: {e}")
        return [], []

def generate_price_chart(stock_symbol: str) -> str:
    """Generate price chart as base64 image"""
    try:
        plt.switch_backend('Agg')  # Ensure non-interactive backend
        plt.figure(figsize=(10, 4))
        hist = yf.Ticker(stock_symbol).history(period="1y")
        plt.figure(figsize=(10, 4))
        plt.plot(hist.index, hist['Close'])
        plt.title(f"{stock_symbol} Price History")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error generating chart: {e}")
        return ""

def generate_analysis_prompt(fundamentals: dict, news_headlines: list, macro_headlines: list) -> str:
    """Generate analysis prompt for Gemini"""
    fundamentals_str = "\n".join([f"{k}: {v}" for k, v in fundamentals.items()])
    news_str = "\n".join(news_headlines) if news_headlines else "No recent news"
    
    return f"""
    Analyze this stock as a senior financial analyst:
    **Analysis Framework to Follow:**
    Note: Only follow this framework for analysis DO NOT return this in output
    1. Valuation: Is the stock overvalued or undervalued based on multiples (PE, P/B, P/S etc.)?
    2. Financial Health: Assess debt levels, liquidity, and profitability metrics.
    3. Growth Potential: Evaluate revenue and earnings growth trends.
    4. Competitive Position: Consider sector and industry position based on available data.
    5. Market Sentiment: Incorporate analyst ratings and recent news sentiment.
    6. Macro Factors: Consider any relevant macroeconomic factors.
    7. Technicals: Briefly consider price trends and moving averages if available.
    
    **Fundamentals:**
    {fundamentals_str}
    
    **Recent News:**
    {news_str}
    
    Note: After analysing based on the above framework and provided fundamentals and latest news, the output should only return the below points:
    1. Health score (1-10) (Note:justify your given healthscore)
    2. Key strengths/risks
    3. Valuation assessment
    5. Macro factors
    4. Recommendation (Buy/Hold/Sell) (Note: justify your Recommendation)

    """

def analyze_with_gemini(prompt: str) -> str:
    """Get analysis from Gemini"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Analysis error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use $PORT or default to 5000
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False for production
