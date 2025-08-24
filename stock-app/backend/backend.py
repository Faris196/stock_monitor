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
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

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
    """Endpoint to analyze a stock with better timeout handling"""
    try:
        data = request.json
        if not data or 'symbol' not in data:
            return jsonify({'error': 'Missing symbol parameter'}), 400
            
        symbol = data['symbol']
        print(f"Starting analysis for: {symbol}")
        
        # Get fundamentals with timeout protection
        try:
            fundamentals = get_stock_fundamentals(symbol)
        except Exception as e:
            print(f"Fundamentals error for {symbol}: {e}")
            fundamentals = None
        
        if not fundamentals:
            return jsonify({
                'error': 'Temporarily unable to fetch stock data. Please try again in a moment.',
                'retryable': True,
                'symbol': symbol
            }), 429
        
        # Get news (with timeout)
        try:
            news_headlines, _ = get_marketaux_news(symbol.split('.')[0])
        except Exception as e:
            print(f"News error for {symbol}: {e}")
            news_headlines = []
        
        # Generate chart (with timeout)
        try:
            chart = generate_price_chart(symbol)
        except Exception as e:
            print(f"Chart error for {symbol}: {e}")
            chart = None
        
        # Generate analysis (with timeout)
        try:
            prompt = generate_analysis_prompt(fundamentals, news_headlines, [])
            analysis = analyze_with_gemini(prompt)
        except Exception as e:
            print(f"Analysis error for {symbol}: {e}")
            analysis = "Unable to generate analysis at this time. Please try again."
        
        # DEBUG: Print what we got from Yahoo Finance
        print("Available keys from Yahoo Finance:")
        for key, value in fundamentals.items():
            print(f"  {key}: {value}")

        # Return partial success if some components failed
        response_data = {
    'fundamentals': [
        # Stock Identity
        {'key': 'Name', 'value': fundamentals.get('Name')},
        {'key': 'Symbol', 'value': symbol},
        {'key': 'Sector', 'value': fundamentals.get('Sector')},
        
        # Financial Metrics
        {'key': 'Market Cap', 'value': format_large_number(fundamentals.get('Market Cap'))},
        {'key': 'Revenue Growth', 'value': format_number(fundamentals.get('Revenue Growth'), 2) + '%' if fundamentals.get('Revenue Growth') else 'N/A'},
        
        # Profitability & Returns
        {'key': 'EPS', 'value': format_number(fundamentals.get('EPS'), 2)},
        {'key': 'Profit Margins', 'value': format_number(fundamentals.get('Profit Margins'), 2) + '%' if fundamentals.get('Profit Margins') else 'N/A'},
        {'key': 'Return On Equity', 'value': format_number(fundamentals.get('Return on Equity'), 2) + '%' if fundamentals.get('Return on Equity') else 'N/A'},
        {'key': 'Dividend Yield', 'value': format_number(fundamentals.get('Dividend Yield'), 2) + '%' if fundamentals.get('Dividend Yield') else 'N/A'},
        
        # Valuation Ratios
        {'key': 'PE Ratio', 'value': format_number(fundamentals.get('PE Ratio'), 2)},
        {'key': 'PEG Ratio', 'value': format_number(fundamentals.get('PEG Ratio'), 2)},
        {'key': 'Price To Book', 'value': format_number(fundamentals.get('Price to Book'), 2)},
        {'key': 'Beta', 'value': format_number(fundamentals.get('Beta'), 2)},
        
        # Financial Health
        {'key': 'Debt To Equity', 'value': format_number(fundamentals.get('Debt to Equity'), 2)},
        
        # Price & Valuation
        {'key': 'Current Price', 'value': format_number(fundamentals.get('Current Price'))},
        {'key': '52 Week High', 'value': format_number(fundamentals.get('52 Week High'))},
        {'key': '52 Week Low', 'value': format_number(fundamentals.get('52 Week Low'))},
        {'key': 'Target Price', 'value': format_number(fundamentals.get('Target Price'))},
        {'key': 'Price Change (%)', 'value': format_number(fundamentals.get('Price Change (%)'), 2) + '%' if fundamentals.get('Price Change (%)') else 'N/A'},
        
        # Trading Info
        {'key': 'Volume', 'value': format_large_number(fundamentals.get('Volume'))}
    ],
    'chart': chart,
    'analysis': analysis,
    'status': 'success',
    'partial': not all([fundamentals, analysis])
}
        
        print(f"Successfully analyzed: {symbol}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Unexpected error in analyze_stock: {e}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.',
            'retryable': True
        }), 500
    
def format_number(value, decimals=2):
    """Format numbers with commas and decimal places"""
    if value is None or value == "N/A":
        return "N/A"
    
    try:
        # Handle both string and numeric values
        num_value = float(value) if isinstance(value, str) else value
        
        if decimals == 0:
            return f"{int(num_value):,}"
        else:
            return f"{num_value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"

def format_large_number(value):
    """Format very large numbers in a readable way (Lakhs, Crores)"""
    if value is None or value == "N/A":
        return "N/A"
    
    try:
        num_value = float(value) if isinstance(value, str) else value
        
        # Indian numbering system: Lakhs (1,00,000) and Crores (1,00,00,000)
        if num_value >= 1_00_00_000:  # 1 Crore (10 Million)
            return f"{num_value/1_00_00_000:.2f} Cr"
        elif num_value >= 1_00_000:  # 1 Lakh (100,000)
            return f"{num_value/1_00_000:.2f} L"
        else:
            return f"{num_value:,.0f}"
    except (ValueError, TypeError):
        return "N/A"
    
def get_stock_fundamentals(stock_symbol: str) -> dict:
    """Fetch comprehensive fundamental data for a stock with maximum metrics"""
    try:
        # Reduced delay to prevent timeouts
        delay = 3 + random.uniform(0, 2)  # 3-5 second delay
        print(f"Waiting {delay:.2f} seconds for {stock_symbol}")
        time.sleep(delay)
        
        stock = yf.Ticker(stock_symbol)
        
        # Get all available info
        try:
            info = stock.info
        except Exception as e:
            print(f"Error getting info for {stock_symbol}: {e}")
            info = {}
        
        # Get historical data for multiple timeframes
        price_change_data = {}
        try:
            # Short-term changes
            hist_1mo = stock.history(period="1mo")
            hist_3mo = stock.history(period="3mo")
            hist_1y = stock.history(period="1y")
            
            # Calculate various price changes
            if not hist_1mo.empty and len(hist_1mo) > 1:
                price_change_data['1mo_change'] = ((hist_1mo['Close'].iloc[-1] - hist_1mo['Close'].iloc[0]) / hist_1mo['Close'].iloc[0]) * 100
            
            if not hist_3mo.empty and len(hist_3mo) > 1:
                price_change_data['3mo_change'] = ((hist_3mo['Close'].iloc[-1] - hist_3mo['Close'].iloc[0]) / hist_3mo['Close'].iloc[0]) * 100
            
            if not hist_1y.empty and len(hist_1y) > 1:
                price_change_data['1y_change'] = ((hist_1y['Close'].iloc[-1] - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0]) * 100
                
        except Exception as e:
            print(f"Error getting history for {stock_symbol}: {e}")
        
        # Get additional data points
        try:
            recommendations = stock.recommendations
            if recommendations is not None and not recommendations.empty:
                latest_recommendation = recommendations.iloc[-1] if len(recommendations) > 0 else {}
        except:
            latest_recommendation = {}
        
        # Comprehensive data extraction
        data = {
            # Basic Information
            "Name": info.get("shortName", info.get("longName", stock_symbol)),
            "Symbol": stock_symbol,
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Exchange": info.get("exchange", "N/A"),
            "Currency": info.get("currency", "N/A"),
            
            # Price Data
            "Current Price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "Previous Close": info.get("previousClose", "N/A"),
            "Open Price": info.get("open", "N/A"),
            "Day High": info.get("dayHigh", "N/A"),
            "Day Low": info.get("dayLow", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            
            # Volume Data
            "Volume": info.get("volume", "N/A"),
            "Average Volume": info.get("averageVolume", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            
            # Valuation Metrics
            "PE Ratio": info.get("trailingPE", info.get("forwardPE", "N/A")),
            "PEG Ratio": info.get("pegRatio", "N/A"),
            "Price to Book": info.get("priceToBook", "N/A"),
            "Price to Sales": info.get("priceToSalesTrailing12Months", "N/A"),
            "EPS": info.get("trailingEps", info.get("forwardEps", "N/A")),
            "EPS Growth": info.get("earningsGrowth", "N/A"),
            
            # Financial Health
            "Debt to Equity": info.get("debtToEquity", "N/A"),
            "Current Ratio": info.get("currentRatio", "N/A"),
            "Quick Ratio": info.get("quickRatio", "N/A"),
            "Return on Equity": info.get("returnOnEquity", "N/A"),
            "Return on Assets": info.get("returnOnAssets", "N/A"),
            "Profit Margins": info.get("profitMargins", "N/A"),
            
            # Dividend Data
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "Dividend Rate": info.get("dividendRate", "N/A"),
            "Payout Ratio": info.get("payoutRatio", "N/A"),
            "Dividend Date": info.get("dividendDate", "N/A"),
            "Ex-Dividend Date": info.get("exDividendDate", "N/A"),
            
            # Growth Metrics
            "Revenue Growth": info.get("revenueGrowth", "N/A"),
            "Earnings Growth": info.get("earningsGrowth", "N/A"),
            "EBITDA": info.get("ebitda", "N/A"),
            "EBITDA Margins": info.get("ebitdaMargins", "N/A"),
            
            # Analyst Ratings
            "Target Price": info.get("targetMeanPrice", "N/A"),
            "Target High Price": info.get("targetHighPrice", "N/A"),
            "Target Low Price": info.get("targetLowPrice", "N/A"),
            "Recommendation": info.get("recommendationKey", "N/A"),
            "Number of Analysts": info.get("numberOfAnalystOpinions", "N/A"),
            
            # Price Performance
            "1 Month Change": round(price_change_data.get('1mo_change', 0), 2),
            "3 Month Change": round(price_change_data.get('3mo_change', 0), 2),
            "1 Year Change": round(price_change_data.get('1y_change', 0), 2),
            "Beta": info.get("beta", "N/A"),
            
            # Additional Metrics
            "Book Value": info.get("bookValue", "N/A"),
            "Enterprise Value": info.get("enterpriseValue", "N/A"),
            "Enterprise to EBITDA": info.get("enterpriseToEbitda", "N/A"),
            "Enterprise to Revenue": info.get("enterpriseToRevenue", "N/A"),
            "Gross Margins": info.get("grossMargins", "N/A"),
            "Operating Margins": info.get("operatingMargins", "N/A"),
            
            # Trading Info
            "Bid": info.get("bid", "N/A"),
            "Ask": info.get("ask", "N/A"),
            "Bid Size": info.get("bidSize", "N/A"),
            "Ask Size": info.get("askSize", "N/A"),
            "Shares Outstanding": info.get("sharesOutstanding", "N/A"),
            "Float Shares": info.get("floatShares", "N/A"),
        }
        
        # Filter out N/A values and clean data
        result = {}
        for key, value in data.items():
            if value not in ["N/A", "", None, "None", "null"]:
                # Convert numbers from strings if needed
                if isinstance(value, str) and value.replace('.', '', 1).replace('-', '', 1).isdigit():
                    try:
                        value = float(value) if '.' in value else int(value)
                    except:
                        pass
                result[key] = value
        
        print(f"Retrieved {len(result)} metrics for {stock_symbol}")
        return result
        
    except Exception as e:
        print(f"Critical error in get_stock_fundamentals for {stock_symbol}: {e}")
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
    1. Show key fundamental metrics
    2. Health score (1-10) (Note:justify your given healthscore)
    3. Key strengths/risks
    4. Valuation assessment
    5. Macro factors
    6. Recommendation (Buy/Hold/Sell) (Note: justify your Recommendation)

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
