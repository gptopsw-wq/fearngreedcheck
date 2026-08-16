# -*- coding: utf-8 -*-
import os
import sys
import json
import re
import webbrowser
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import io

# Import the HTML generator
import dashboard_template

def fetch_cnn_data():
    """
    Fetches Fear & Greed Index data from CNN Business.
    """
    print("Fetching US Fear & Greed Index from CNN...")
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching CNN data: {e}")
        return None

def fetch_kr_data():
    """
    Fetches Fear & Greed Index data from KOSPI FGI.
    """
    print("Fetching Korea Fear & Greed Index from KOSPI FGI...")
    url = "https://kospifgi.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Search Next.js script payload
        scripts = soup.find_all('script')
        for s in scripts:
            text = s.string
            if text and "initialLatest" in text:
                # Find start index of JSON
                start_idx = text.find('{\\"initialPreset\\"')
                if start_idx == -1:
                    continue
                
                # Scan brace balance to find end of JSON
                brace_count = 0
                end_idx = -1
                for i in range(start_idx, len(text)):
                    char = text[i]
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i
                            break
                
                if end_idx != -1:
                    escaped_json = text[start_idx:end_idx+1]
                    # Unescape quotes and backslashes
                    unescaped_json = escaped_json.replace('\\"', '"').replace('\\\\', '\\')
                    return json.loads(unescaped_json)
        
        print("Error: Next.js script payload containing initialLatest not found.")
        return None
    except Exception as e:
        print(f"Error fetching KOSPI FGI data: {e}")
        return None

def align_history(us_hist_data, kr_hist_list):
    """
    Aligns US and Korea historical FGI data by date.
    Returns sorted dates, aligned US scores, and aligned KR scores.
    """
    # Parse US history: convert ms timestamp to YYYY-MM-DD
    us_history = {}
    for pt in us_hist_data.get('data', []):
        ts_ms = pt.get('x')
        score = pt.get('y')
        if ts_ms is not None and score is not None:
            # Convert millisecond timestamp to local date string (UTC+9 for KR comparison)
            date_str = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone(timedelta(hours=9))).strftime('%Y-%m-%d')
            us_history[date_str] = score
            
    # Sort KR history by date
    kr_history = sorted(kr_hist_list, key=lambda x: x.get('date', ''))
    
    # We will align historical data based on Korea trading dates
    aligned_dates = []
    aligned_us_scores = []
    aligned_kr_scores = []
    
    # Find overlapping timeline
    for pt in kr_history:
        date_str = pt.get('date')
        kr_score = pt.get('fgi_score')
        if not date_str or kr_score is None:
            continue
            
        aligned_dates.append(date_str)
        aligned_kr_scores.append(kr_score)
        
        # Look up US score for the same date. If missing (e.g. US holiday or weekend),
        # we will use the most recent previous US score.
        us_score = us_history.get(date_str)
        if us_score is None:
            # Find closest previous date in US history
            prev_dates = [d for d in us_history.keys() if d < date_str]
            if prev_dates:
                closest_prev_date = max(prev_dates)
                us_score = us_history[closest_prev_date]
            else:
                us_score = 50.0  # Default neutral if no previous date found
        aligned_us_scores.append(us_score)
        
    return aligned_dates, aligned_us_scores, aligned_kr_scores

def fetch_us_10y_csv():
    """
    Fetches historical 10-year US Fear & Greed Index from GitHub.
    """
    print("Fetching 10-year US Fear & Greed Index from GitHub archive...")
    url = "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/master/fear-greed.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        return df
    except Exception as e:
        print(f"Warning: Failed to fetch 10-year US FGI: {e}")
        return None

def calculate_kr_10y_proxy():
    """
    Calculates KOSPI FGI proxy for the past 10 years using a 4-factor model:
    1) Market Momentum: KOSPI vs 125MA
    2) Market Volatility: 20-day annualized historical volatility of KOSPI
    3) Safe Haven Demand: KODEX 200 vs KODEX 3Y Treasury ETF
    4) Exchange Rate: USD/KRW vs 125MA
    Scaled globally to map historical bounds to 0-100 (Correlation with actual KOSPI FGI: ~0.87).
    """
    print("Calculating 10-year Korea FGI Proxy from historical market data...")
    start_date = "2016-08-16"
    end_date = datetime.now().strftime('%Y-%m-%d')
    try:
        kospi = fdr.DataReader('^KS11', start_date, end_date)
        usdkrw = fdr.DataReader('USD/KRW', start_date, end_date)
        kodex200 = fdr.DataReader('069500', start_date, end_date)
        kodex3y = fdr.DataReader('114820', start_date, end_date)
        
        df = pd.DataFrame(index=kospi.index)
        df['kospi'] = kospi['Close']
        df['usdkrw'] = usdkrw['Close']
        df['kodex200'] = kodex200['Close']
        df['kodex3y'] = kodex3y['Close']
        df = df.ffill().bfill()
        
        # 1) Momentum
        df['kospi_125ma'] = df['kospi'].rolling(window=125).mean()
        df['mom_ratio'] = df['kospi'] / df['kospi_125ma']
        
        # 2) Volatility
        df['kospi_returns'] = df['kospi'].pct_change()
        df['volatility'] = df['kospi_returns'].rolling(window=20).std() * np.sqrt(250)
        
        # 3) Exchange rate
        df['usdkrw_125ma'] = df['usdkrw'].rolling(window=125).mean()
        df['fx_ratio'] = df['usdkrw'] / df['usdkrw_125ma']
        
        # 4) Safe Haven Demand
        df['stock_ret_20d'] = df['kodex200'].pct_change(periods=20)
        df['bond_ret_20d'] = df['kodex3y'].pct_change(periods=20)
        df['safe_haven_spread'] = df['stock_ret_20d'] - df['bond_ret_20d']
        
        df = df.dropna()
        
        # Global scaling
        def global_scale(series, invert=False):
            s_min = series.min()
            s_max = series.max()
            if s_max == s_min:
                return series * 0 + 50.0
            scaled = (series - s_min) / (s_max - s_min) * 100
            if invert:
                return 100 - scaled
            return scaled
            
        df['mom_score'] = global_scale(df['mom_ratio'])
        df['vol_score'] = global_scale(df['volatility'], invert=True)
        df['fx_score'] = global_scale(df['fx_ratio'], invert=True)
        df['safe_haven_score'] = global_scale(df['safe_haven_spread'])
        
        df['proxy_score'] = df[['mom_score', 'vol_score', 'fx_score', 'safe_haven_score']].mean(axis=1)
        return df[['proxy_score']]
    except Exception as e:
        print(f"Warning: Failed to calculate 10-year KR FGI proxy: {e}")
        return None

def process_10y_history(us_df, kr_df):
    """
    Downsamples daily 10-year US and KR proxy data to weekly (W-SUN) and merges them.
    This reduces payload size and renders a cleaner long-term chart.
    """
    if us_df is None or kr_df is None:
        print("Warning: Skipping 10-year timeline due to missing data.")
        return [], [], []
        
    print("Downsampling 10-year data to weekly series...")
    try:
        kr_weekly = kr_df.resample('W').last()
        us_weekly = us_df[['Fear Greed']].resample('W').last()
        
        merged = pd.DataFrame(index=kr_weekly.index)
        merged['kr'] = kr_weekly['proxy_score']
        merged['us'] = us_weekly['Fear Greed']
        merged = merged.ffill().bfill().dropna()
        
        dates = merged.index.strftime('%Y-%m-%d').tolist()
        kr_scores = merged['kr'].round(1).tolist()
        us_scores = merged['us'].round(1).tolist()
        return dates, us_scores, kr_scores
    except Exception as e:
        print(f"Warning: Error in downsampling 10-year history: {e}")
        return [], [], []

def process_data(us_data, kr_data):
    """
    Processes the raw scraped data into the final structured format for the HTML.
    """
    processed = {}
    
    # Current timestamp
    processed['timestamp'] = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S')
    
    # Process US current
    us_curr = us_data.get('fear_and_greed', {})
    processed['us_current'] = {
        'score': us_curr.get('score', 50.0),
        'rating': us_curr.get('rating', 'neutral'),
        'previous_close': us_curr.get('previous_close', 50.0),
        'previous_1_week': us_curr.get('previous_1_week', 50.0),
        'previous_1_month': us_curr.get('previous_1_month', 50.0),
        'previous_1_year': us_curr.get('previous_1_year', 50.0)
    }
    
    # Process KR current
    kr_curr = kr_data.get('initialLatest', {})
    kr_hist = kr_data.get('initialHistory', [])
    
    # Retrieve previous values from KOSPI FGI history list (sorted ascending)
    kr_hist_sorted = sorted(kr_hist, key=lambda x: x.get('date', ''))
    
    previous_close = kr_curr.get('fgi_score', 50.0)
    previous_1_w = kr_curr.get('fgi_score', 50.0)
    previous_1_m = kr_curr.get('fgi_score', 50.0)
    previous_3_m = kr_curr.get('fgi_score', 50.0)
    
    if len(kr_hist_sorted) >= 1:
        previous_close = kr_hist_sorted[-1].get('fgi_score', previous_close)
    if len(kr_hist_sorted) >= 5:
        previous_1_w = kr_hist_sorted[-5].get('fgi_score', previous_1_w)
    if len(kr_hist_sorted) >= 20:
        previous_1_m = kr_hist_sorted[-20].get('fgi_score', previous_1_m)
    if len(kr_hist_sorted) > 0:
        previous_3_m = kr_hist_sorted[0].get('fgi_score', previous_3_m)
        
    processed['kr_current'] = {
        'score': kr_curr.get('fgi_score', 50.0),
        'rating': kr_curr.get('regime', 'neutral'),
        'date': kr_curr.get('date', ''),
        'previous_close': previous_close,
        'previous_1_week': previous_1_w,
        'previous_1_month': previous_1_m,
        'previous_3_month': previous_3_m
    }
    
    # Process 3M History Aligned
    dates, us_scores, kr_scores = align_history(us_data.get('fear_and_greed_historical', {}), kr_hist)
    processed['history_dates'] = dates
    processed['us_history_scores'] = us_scores
    processed['kr_history_scores'] = kr_scores
    
    # US Sub-components mapping
    us_comps_raw = [
        ('market_momentum_sp500', 'Market Momentum (시장 모멘텀)'),
        ('stock_price_strength', 'Stock Price Strength (주가 강도)'),
        ('stock_price_breadth', 'Stock Price Breadth (주가 폭)'),
        ('put_call_options', 'Put and Call Options (풋/콜 옵션)'),
        ('market_volatility_vix', 'Market Volatility (시장 변동성 - VIX)'),
        ('junk_bond_demand', 'Junk Bond Demand (정크본드 수요)'),
        ('safe_haven_demand', 'Safe Haven Demand (안전자산 선호)')
    ]
    processed['us_components'] = []
    for key, name in us_comps_raw:
        comp_data = us_data.get(key, {})
        processed['us_components'].append({
            'key': key,
            'name': name,
            'score': comp_data.get('score', 50.0),
            'rating': comp_data.get('rating', 'neutral')
        })
        
    # KR Sub-components mapping
    kr_comps_raw = [
        ('momentum', 'KOSPI Momentum (시장 모멘텀)'),
        ('strength', 'Stock Strength (주가 강도)'),
        ('breadth', 'Stock Breadth (주가 폭)'),
        ('put_call', 'Put and Call Options (풋/콜 옵션)'),
        ('volatility', 'Market Volatility (변동성 - V-KOSPI)'),
        ('junk_bond', 'Credit Spread (신용 스프레드)'),
        ('safe_haven', 'Safe Haven Demand (안전자산 선호)'),
        ('fx', 'FX Rate (원/달러 환율)')
    ]
    processed['kr_components'] = []
    kr_comps_dict = {c.get('key'): c for c in kr_data.get('initialComponentCharts', [])}
    
    for key, name in kr_comps_raw:
        comp_data = kr_comps_dict.get(key, {})
        processed['kr_components'].append({
            'key': key,
            'name': name,
            'score': comp_data.get('latest_score', 50.0),
            'rating': comp_data.get('latest_regime', 'neutral')
        })
        
    # KR Analysis
    kr_analysis = kr_data.get('initialAnalysis', {})
    kr_output = kr_analysis.get('output_json', {})
    processed['kr_analysis'] = {
        'summary': kr_analysis.get('summary', '요약 정보가 없습니다.'),
        'confidence': kr_analysis.get('confidence', 0.5),
        'risks': kr_output.get('risks', []),
        'claims': kr_output.get('claims', [])
    }
    
    return processed

def main():
    print("==================================================")
    print(" 한-미 공포 탐욕 지수 시각화 대시보드 생성기")
    print("==================================================")
    
    # 1. Fetch data
    us_raw = fetch_cnn_data()
    if not us_raw:
        print("Failed to fetch US Fear & Greed Index. Exiting.")
        sys.exit(1)
        
    kr_raw = fetch_kr_data()
    if not kr_raw:
        print("Failed to fetch KR Fear & Greed Index. Exiting.")
        sys.exit(1)
        
    # 2. Process recent 3m data
    print("Processing and aligning recent 3-month data...")
    processed_data = process_data(us_raw, kr_raw)
    
    # 3. Fetch and process 10-year historical data
    us_10y_df = fetch_us_10y_csv()
    kr_10y_df = calculate_kr_10y_proxy()
    
    dates_10y, us_10y_scores, kr_10y_scores = process_10y_history(us_10y_df, kr_10y_df)
    
    # Calculate Averages for 10-year view
    if us_10y_scores and kr_10y_scores:
        us_10y_avg = float(np.mean(us_10y_scores))
        kr_10y_avg = float(np.mean(kr_10y_scores))
    else:
        us_10y_avg = 50.0
        kr_10y_avg = 50.0
    
    # Inject 10y history and averages into processed_data
    processed_data['history_10y_dates'] = dates_10y
    processed_data['us_history_10y_scores'] = us_10y_scores
    processed_data['kr_history_10y_scores'] = kr_10y_scores
    processed_data['us_history_10y_avg'] = round(us_10y_avg, 1)
    processed_data['kr_history_10y_avg'] = round(kr_10y_avg, 1)
    
    # 4. Generate HTML content
    print("Generating HTML dashboard...")
    html_content = dashboard_template.generate_html(processed_data)
    
    # 5. Write to dashboard.html in current directory
    output_path = os.path.abspath("dashboard.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Success! Dashboard created at: {output_path}")
    print("Opening dashboard in default browser...")
    
    # 6. Open in browser
    webbrowser.open("file://" + output_path)
    print("Done!")

if __name__ == "__main__":
    main()
