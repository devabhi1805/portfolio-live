from flask import Flask, request, jsonify, render_template
import os
import pdfplumber
import re
import json
import random
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import threading
import yfinance as yf

app = Flask(__name__)
DATA_FILE = 'portfolio_data.json'
MAPPING_FILE = "symbol_mapping.json"
mapping_lock = threading.Lock()

SECTOR_KNOWLEDGE = {
    "Healthcare/Pharma": {
        "peers": ["Sun Pharma", "Cipla", "Dr. Reddy's", "Divi's Labs", "Apollo Hospitals"],
        "about": "Engaged in pharmaceutical manufacturing, R&D, and healthcare services.",
        "moat": "R&D Monopolies & Patents",
        "risk": "Strict FDA regulations and drug trial failures."
    },
    "Chemicals": {
        "peers": ["SRF", "Aarti Industries", "Deepak Nitrite", "Tata Chemicals", "Pidilite"],
        "about": "Involved in specialty chemicals, agrochemicals, and polymers.",
        "moat": "High Switching Costs & Scale",
        "risk": "Raw material price volatility (crude oil) and environmental compliance."
    },
    "Technology/IT": {
        "peers": ["TCS", "Infosys", "Wipro", "HCL Tech", "Tech Mahindra"],
        "about": "Provides IT services, consulting, software, and digital transformation.",
        "moat": "High Switching Costs & Talent Pool",
        "risk": "Global recession impacting IT budgets and AI disruption."
    },
    "Engineering & Capital Goods": {
        "peers": ["Larsen & Toubro", "Siemens", "ABB India", "BHEL", "Cummins India"],
        "about": "Manufactures heavy machinery, electrical equipment, and infrastructure construction.",
        "moat": "High Entry Barriers & Execution",
        "risk": "Capital intensive and highly sensitive to economic cycles."
    },
    "Renewable Energy": {
        "peers": ["Tata Power", "Adani Green", "Suzlon", "Borosil Renewables", "Inox Wind"],
        "about": "Focuses on solar, wind power generation, and green infrastructure.",
        "moat": "Government Subsidies & Long-term PPAs",
        "risk": "Policy changes and heavy upfront capital requirement."
    },
    "Consumer Goods/Retail": {
        "peers": ["HUL", "ITC", "Titan", "Avenue Supermarts (DMart)", "Nestle India"],
        "about": "FMCG, retail, consumer durables, and daily-use products.",
        "moat": "Brand Loyalty & Distribution Network",
        "risk": "Inflation impacting consumer demand."
    },
    "Metals & Mining": {
        "peers": ["Tata Steel", "JSW Steel", "Hindalco", "Vedanta", "Coal India"],
        "about": "Involved in iron ore extraction, steel, and alloy production.",
        "moat": "Cost Leadership & Captive Mines",
        "risk": "Global commodity cycles and environmental regulations."
    },
    "Logistics": {
        "peers": ["Blue Dart", "Delhivery", "TCI Express", "Mahindra Logistics", "VRL Logistics"],
        "about": "Provides supply chain and B2B/B2C transportation solutions.",
        "moat": "Network Density Advantage",
        "risk": "Fuel price volatility and economic slowdowns."
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def guess_sector(name):
    name_lower = name.lower()
    if any(x in name_lower for x in ["health", "pharma", "medical", "bio", "care", "suven", "wockhardt", "amanta"]):
        return "Healthcare/Pharma"
    elif any(x in name_lower for x in ["chem", "aether", "neochem", "polymer", "sacheerome", "cwd"]):
        return "Chemicals"
    elif any(x in name_lower for x in ["tech", "soft", "info", "net", "e2e", "infinity", "data", "pelatro", "bhadora"]):
        return "Technology/IT"
    elif any(x in name_lower for x in ["engg", "engineering", "power", "infra", "wire", "cable", "motor", "greaves", "danish", "forge", "cnc"]):
        return "Engineering & Capital Goods"
    elif any(x in name_lower for x in ["energy", "solar", "green", "enviro", "sun drops", "clean max"]):
        return "Renewable Energy"
    elif any(x in name_lower for x in ["retail", "jewel", "food", "fashion", "agro", "safe", "s d", "bluestone", "dee"]):
        return "Consumer Goods/Retail"
    elif any(x in name_lower for x in ["steel", "metal", "iron", "alloy", "jindal", "shri"]):
        return "Metals & Mining"
    elif any(x in name_lower for x in ["transport", "logistics", "shadowfax", "mover", "sanghvi"]):
        return "Logistics"
    else:
        return "Engineering & Capital Goods"

def enrich_stock_data(name, qty, curr_price, today_gain, value):
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', name)
    
    sector = guess_sector(name)
    knowledge = SECTOR_KNOWLEDGE[sector]
    
    return {
        "name": name,
        "sector": sector,
        "qty": qty,
        "price": curr_price,
        "change": today_gain,
        "value": value,
        "about": f"{name} is active in the {sector} sector. {knowledge['about']}",
        "moat": knowledge["moat"],
        "risk": knowledge["risk"],
        "peers": knowledge["peers"],
        "fundamentals": {
            "Market Cap": f"Rs {random.randint(100, 10000)} Cr (Est.)",
            "P/E Ratio": round(random.uniform(10, 80), 1),
            "ROE": f"{round(random.uniform(5, 35), 1)}%",
            "Debt to Equity": round(random.uniform(0, 2), 2)
        },
        "news": [
            f"Analysts hold positive outlook for {name}.",
            f"{name} recently discussed future strategies."
        ]
    }

def get_symbol_mapping(company_name):
    with mapping_lock:
        mapping = {}
        if os.path.exists(MAPPING_FILE):
            try:
                with open(MAPPING_FILE, 'r') as f:
                    mapping = json.load(f)
            except:
                pass
        if company_name in mapping:
            return mapping[company_name]
            
    try:
        search_query = company_name.replace(" ", "+")
        search_url = f"https://www.screener.in/api/company/search/?q={search_query}&v=3"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(search_url, headers=headers, timeout=5)
        
        if res.status_code == 429:
            result = {"status": "error", "message": "Rate limited by data source. Try again."}
        elif res.status_code != 200:
            result = {"status": "error", "message": f"API returned {res.status_code}"}
        else:
            data = res.json()
            if not data:
                result = {"status": "error", "message": "No matching symbol found."}
            elif len(data) == 1:
                symbol = data[0]['url'].split('/')[2]
                result = {"status": "resolved", "symbol": f"{symbol}.NS"}
            else:
                first_name = data[0]['name'].lower().replace('ltd', '').replace('limited', '').strip()
                query_name = company_name.lower().replace('ltd', '').replace('limited', '').strip()
                if first_name == query_name or query_name in first_name:
                    symbol = data[0]['url'].split('/')[2]
                    result = {"status": "resolved", "symbol": f"{symbol}.NS"}
                else:
                    result = {"status": "ambiguous", "message": "Multiple matches found. Cannot determine exact symbol."}
    except requests.exceptions.Timeout:
        result = {"status": "error", "message": "Mapping request timed out."}
    except Exception as e:
        result = {"status": "error", "message": "Network error during mapping."}
        
    if result["status"] in ["resolved", "ambiguous"]:
        with mapping_lock:
            if os.path.exists(MAPPING_FILE):
                try:
                    with open(MAPPING_FILE, 'r') as f:
                        mapping = json.load(f)
                except:
                    pass
            mapping[company_name] = result
            with open(MAPPING_FILE, 'w') as f:
                json.dump(mapping, f, indent=4)
                
    return result

def fetch_yfinance_price(symbol):
    try:
        t = yf.Ticker(symbol)
        if 'lastPrice' in t.fast_info:
            return float(t.fast_info['lastPrice'])
        elif 'previousClose' in t.fast_info:
            return float(t.fast_info['previousClose'])
    except Exception:
        pass
    return None

def process_stock_refresh(s):
    m = get_symbol_mapping(s['name'])
    s.pop('refresh_error', None)
    
    if m.get('status') == 'resolved':
        symbol = m['symbol']
        new_price = fetch_yfinance_price(symbol)
        if new_price is not None:
            s['price'] = round(new_price, 2)
            s['value'] = round(new_price * s['qty'], 2)
        else:
            s['refresh_error'] = f"Data unavailable for {symbol}."
    else:
        s['refresh_error'] = m.get('message', 'Symbol mapping failed.')
    return s

def parse_pdf(pdf_file_path):
    stocks = []
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
                
            lines = text.split('\n')
            
            for i in range(2, len(lines)):
                line3 = lines[i].strip()
                percents = re.findall(r'-?[\d,]+\.\d{2}%', line3)
                if len(percents) >= 2:
                    line2 = lines[i-1].strip()
                    line1 = lines[i-2].strip()
                    
                    try:
                        qty_match = re.match(r'^(\d+)\s', line1)
                        if not qty_match: continue
                        qty = int(qty_match.group(1))
                        
                        match2 = re.match(r'^([A-Za-z0-9\-\&\.\(\)]+)\s+([\d,\.\-]+)\s+([\d,\.\-]+)\s+([\d,\.\-]+)', line2)
                        if not match2: continue
                        
                        name = match2.group(1).strip()
                        curr_price = float(match2.group(3).replace(',', ''))
                        val = float(match2.group(4).replace(',', ''))
                        
                        today_gain = float(percents[0].replace('%', ''))
                        
                        stocks.append(enrich_stock_data(name, qty, curr_price, today_gain, val))
                    except Exception as e:
                        continue

    except Exception as e:
        print(f"Error parsing PDF: {e}")
        
    return stocks

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)
        
        stocks = parse_pdf(filepath)
        if not stocks:
            return jsonify({"error": "Format not found."}), 400
            
        save_data(stocks) # Save to JSON
        return jsonify({"stocks": stocks})
    return jsonify({"error": "Format not found."}), 400

@app.route('/refresh_prices', methods=['POST'])
def refresh_prices():
    stocks = load_data()
    if not stocks:
        return jsonify({"error": "No stocks found to refresh."}), 400
        
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            updated_stocks = list(executor.map(process_stock_refresh, stocks))
            
        save_data(updated_stocks) # Persist the new live prices
        return jsonify({"stocks": updated_stocks})
    except Exception as e:
        print(f"Refresh prices crashed: {e}")
        return jsonify({"error": "Failed to refresh prices. Please try again."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
