# gemini api key - AIzaSyA5sJKDZ9khlusbuwjGyVzqZcjmoNM0uqU
# marketaux_api_key - 4UDxFAYYalVR8j9MAEza7RdEBlu0dgrG8lrXSes6

import yfinance as yf
import requests
import google.generativeai as genai
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List, Optional

# Configuration
genai.configure(api_key="AIzaSyA5sJKDZ9khlusbuwjGyVzqZcjmoNM0uqU")
MARKETAUX_API_KEY = "4UDxFAYYalVR8j9MAEza7RdEBlu0dgrG8lrXSes6"

# Constants
METRICS_TO_DISPLAY = [
    "Current Price", "Market Cap", "PE Ratio", "Price to Book", 
    "Dividend Yield", "Debt to Equity", "Revenue Growth", "Price Change (%)"
]

def get_stock_fundamentals(stock_symbol: str) -> Dict[str, float]:
    """Fetch comprehensive fundamental data for a stock"""
    try:
        stock = yf.Ticker(stock_symbol)
        info = stock.info
        
        # Get historical data for trend analysis
        hist = stock.history(period="1y")
        if not hist.empty:
            price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
        else:
            price_change = 0
        
        data = {
            # Basic Info
            "Name": info.get("shortName", stock_symbol),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            
            # Valuation Metrics
            "Current Price": info.get("currentPrice", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "Forward PE": info.get("forwardPE", "N/A"),
            "Price to Book": info.get("priceToBook", "N/A"),
            "Price to Sales": info.get("priceToSalesTrailing12Months", "N/A"),
            "Enterprise Value": info.get("enterpriseValue", "N/A"),
            
            # Profitability Metrics
            "Return on Equity": info.get("returnOnEquity", "N/A"),
            "Return on Assets": info.get("returnOnAssets", "N/A"),
            "Profit Margins": info.get("profitMargins", "N/A"),
            "Operating Margins": info.get("operatingMargins", "N/A"),
            
            # Growth Metrics
            "Earnings Growth": info.get("earningsGrowth", "N/A"),
            "Revenue Growth": info.get("revenueGrowth", "N/A"),
            "Quarterly Revenue Growth": info.get("quarterlyRevenueGrowth", "N/A"),
            
            # Financial Health
            "Debt to Equity": info.get("debtToEquity", "N/A"),
            "Current Ratio": info.get("currentRatio", "N/A"),
            "Quick Ratio": info.get("quickRatio", "N/A"),
            
            # Dividends
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "Payout Ratio": info.get("payoutRatio", "N/A"),
            
            # Market Sentiment
            "Analyst Recommendation": info.get("recommendationKey", "N/A"),
            "Number of Analysts": info.get("numberOfAnalystOpinions", "N/A"),
            
            # Price Performance
            "Price Change (%)": round(price_change, 2),
            "Beta": info.get("beta", "N/A"),
            "50 Day Average": info.get("fiftyDayAverage", "N/A"),
            "200 Day Average": info.get("twoHundredDayAverage", "N/A"),
        }
        
        return {k: v for k, v in data.items() if v != "N/A"}
    except Exception as e:
        print(f"Error fetching fundamentals: {e}")
        return {}

def get_marketaux_news(stock_symbol: str, num_results: int = 5) -> Tuple[List[str], List[str]]:
    """Fetch recent news headlines for a stock and general market news"""
    try:
        # Stock-specific news
        base_symbol = stock_symbol.split('.')[0]  # Remove .NS if present
        url = f"https://api.marketaux.com/v1/news/all?symbols={base_symbol}&filter_entities=true&language=en&api_token={MARKETAUX_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("data", [])
        headlines = [f"{article['title']} ({article['published_at'][:10]})" for article in articles[:num_results]]
        
        # Macro news (general business/economic headlines)
        macro_url = f"https://api.marketaux.com/v1/news/all?entities=economy&language=en&api_token={MARKETAUX_API_KEY}"
        macro_response = requests.get(macro_url, timeout=10)
        macro_response.raise_for_status()
        macro_articles = macro_response.json().get("data", [])
        macro_headlines = [f"{article['title']} ({article['published_at'][:10]})" for article in macro_articles[:3]]
        
        return headlines, macro_headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return [], []

def generate_analysis_prompt(stock_fundamentals: Dict, news_headlines: List[str], macro_headlines: List[str]) -> str:
    """Generate a comprehensive prompt for the LLM analysis"""
    # Format fundamentals data
    fundamentals_str = "\n".join([f"{k}: {v}" for k, v in stock_fundamentals.items()])
    
    # Format news data
    news_str = "\n".join(news_headlines) if news_headlines else "No recent company-specific news found"
    macro_str = "\n".join(macro_headlines) if macro_headlines else "No relevant macroeconomic news found"
    
    # Create detailed prompt with analysis framework
    prompt = f"""
    You are a senior financial analyst with 20 years of experience evaluating stocks. 
    Analyze the following stock comprehensively and provide a detailed health assessment.
    
    **Analysis Framework to Follow:**
    1. Valuation: Is the stock overvalued or undervalued based on multiples (PE, P/B, P/S etc.)?
    2. Financial Health: Assess debt levels, liquidity, and profitability metrics.
    3. Growth Potential: Evaluate revenue and earnings growth trends.
    4. Competitive Position: Consider sector and industry position based on available data.
    5. Market Sentiment: Incorporate analyst ratings and recent news sentiment.
    6. Macro Factors: Consider any relevant macroeconomic factors.
    7. Technicals: Briefly consider price trends and moving averages if available.
    
    **Stock Fundamentals:**
    {fundamentals_str}
    
    **Recent Company News:**
    {news_str}
    
    **Relevant Macro News:**
    {macro_str}
    
    **Required Output Format:**
    1. Summary (2-3 sentences)
    2. Strengths (bulleted list)
    3. Risks (bulleted list)
    4. Valuation Assessment (undervalued/fair/overvalued)
    5. Health Score (1-10, 10 being healthiest)
    6. Recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
    7. Key Metrics to Monitor (list 3-5 most important metrics for this stock)
    
    **Additional Guidelines:**
    - Be specific and quantitative where possible
    - Highlight any red flags or exceptional positives
    - Compare to industry averages when possible
    - Consider both short-term and long-term perspectives
    """
    
    return prompt

def analyze_with_gemini(prompt: str) -> str:
    """Analyze the stock data using Gemini"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Analysis error: {str(e)}"

def display_key_metrics(stock_fundamentals: Dict) -> None:
    """Display key metrics in a readable format"""
    print("\nKey Metrics:")
    for metric in METRICS_TO_DISPLAY:
        if metric in stock_fundamentals:
            print(f"{metric}: {stock_fundamentals[metric]}")

def plot_history(stock_symbol: str):
    """Plot price history in non-blocking mode"""
    try:
        print("Generating price chart...")
        plt.switch_backend('Qt5Agg')  # Use Qt backend for non-blocking
        hist = yf.Ticker(stock_symbol).history(period="1y")
        if not hist.empty:
            plt.figure(figsize=(10, 4))
            plt.plot(hist.index, hist['Close'])
            plt.title(f"{stock_symbol} Price History")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.grid(True)
            plt.show(block=False)  # Non-blocking show
            print("Chart displayed (program continues running)")
    except Exception as e:
        print(f"Couldn't plot history: {str(e)}")

if __name__ == "__main__":
    try:
        stock_input = input("Enter stock symbol (e.g. HCLTECH.NS): ").strip()
        yf_input = stock_input if stock_input.endswith('.NS') else stock_input + ".NS"
        
        print(f"\nFetching data for {stock_input}...")
        
        # Get all data
        fundamentals = get_stock_fundamentals(yf_input)
        news_headlines, macro_headlines = get_marketaux_news(stock_input)
        
        if not fundamentals:
            print("Failed to get stock data. Please check the symbol and try again.")
            exit()
        
        # Display basic info
        print(f"\nCompany: {fundamentals.get('Name', 'N/A')}")
        print(f"Sector: {fundamentals.get('Sector', 'N/A')}")
        print(f"Industry: {fundamentals.get('Industry', 'N/A')}")
        
        display_key_metrics(fundamentals)
        plot_history(yf_input)
        
        # Generate and display analysis
        print("\nGenerating comprehensive analysis...")
        prompt = generate_analysis_prompt(fundamentals, news_headlines, macro_headlines)
        analysis = analyze_with_gemini(prompt)
        
        print("\n----- COMPREHENSIVE STOCK ANALYSIS -----")
        print(analysis)
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")