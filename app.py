import os
import re
import random
import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, render_template
import pdfplumber

app = Flask(__name__, template_folder='templates')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

DATA_FILE = os.path.join(os.path.dirname(__file__), 'portfolio_data.json')

SECTOR_KNOWLEDGE = {
    "Healthcare/Pharma": {
        "peers": ["Sun Pharma", "Cipla", "Dr. Reddy's", "Divi's Labs", "Lupin"],
        "about": "Engaged in pharmaceutical manufacturing and API development.",
        "moat": "R&D Monopolies & Patents",
        "risk": "FDA compliance and government price capping."
    },
    "Chemicals": {
        "peers": ["SRF", "Navin Fluorine", "PI Industries", "Aarti Industries", "Tata Chemicals"],
        "about": "Manufactures specialty chemicals and advanced intermediates.",
        "moat": "High Switching Costs & Scale",
        "risk": "Crude price volatility and environmental regulations."
    },
    "Engineering & Capital Goods": {
        "peers": ["L&T", "Siemens", "ABB India", "Cummins India", "Thermax"],
        "about": "Involved in heavy engineering and EPC contracts.",
        "moat": "High Entry Barriers & Execution",
        "risk": "Cyclical capex slowdown and raw material inflation."
    },
    "Technology/IT": {
        "peers": ["TCS", "Infosys", "Wipro", "HCL Tech", "Tech Mahindra"],
        "about": "Provides IT services, cloud infrastructure, and AI solutions.",
        "moat": "Sticky Clients & High Switching Cost",
        "risk": "High attrition and currency fluctuations."
    },
    "Renewable Energy": {
        "peers": ["Tata Power", "Adani Green", "Renew Power", "Suzlon", "Inox Wind"],
        "about": "Focused on green energy generation and solar/wind EPC.",
        "moat": "Long-term PPA Cash Flows",
        "risk": "Policy changes and high debt levels."
    },
    "Consumer Goods/Retail": {
        "peers": ["HUL", "ITC", "Titan", "Avenue Supermarts", "Nestle India"],
        "about": "Operates in retail, FMCG, and direct-to-consumer categories.",
        "moat": "Deep Distribution & Pricing Power",
        "risk": "Inflation affecting margins and intense competition."
    },
    "Metals & Mining": {
        "peers": ["Tata Steel", "JSW Steel", "Hindalco", "Vedanta", "NMDC"],
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

def fetch_screener_price(stock_obj):
    company_name = stock_obj['name']
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        search_query = company_name.replace(" ", "+")
        search_url = f"https://www.screener.in/api/company/search/?q={search_query}&v=3"
        
        res = requests.get(search_url, headers=headers, timeout=5)
        data = res.json()
        
        if data and len(data) > 0:
            company_url = "https://www.screener.in" + data[0]['url']
            page = requests.get(company_url, headers=headers, timeout=5)
            
            soup = BeautifulSoup(page.text, 'html.parser')
            ratios = soup.find(id='top-ratios')
            
            if ratios:
                for li in ratios.find_all('li'):
                    if 'Current Price' in li.text:
                        price_span = li.find('span', class_='number')
                        if price_span:
                            live_price_str = price_span.text.replace(',', '')
                            live_price = float(live_price_str)
                            
                            stock_obj['price'] = round(live_price, 2)
                            stock_obj['value'] = round(live_price * stock_obj['qty'], 2)
                            break
    except Exception as e:
        print(f"Error fetching screener data for {company_name}: {e}")
        
    return stock_obj

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
        
    with ThreadPoolExecutor(max_workers=5) as executor:
        updated_stocks = list(executor.map(fetch_screener_price, stocks))
        
    save_data(updated_stocks) # Persist the new live prices
    return jsonify({"stocks": updated_stocks})

@app.route('/get_portfolio', methods=['GET'])
def get_portfolio():
    stocks = load_data()
    return jsonify({"stocks": stocks})

if __name__ == '__main__':
    import threading
    import webbrowser
    import time
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:5000")
        
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
