import json
import random

# Sample extracted from PDF OCR
raw_data = """Aakaar Medical Technologies
Aether Industries
Amanta Healthcare
Anawil Wire and Engineering
Aprameya Engineering
Bai-Kakaji Polymers
Bhadora Industries
BlueStone Jewellery and Lifestyle
Bondada Engineering
Chetana Education
Clay Craft India
Clean Max Enviro Energy Solutions
Credent Connect N Care
Current Infraprojects
CWD Ltd
Danish Power
DEE Development Engineers
Dev Accelerator
Dhara Rail Projects
E Factor Experiences
E to E Transportation Infrastructure
E2E Networks
Ecoline Exim
Forge Auto International
Glen Industries
GNG Electronics
Greaves Cotton
Horizon Reclaim (India)
Indian Metals & Ferro Alloys
Infinity Infoway
Influx Healthtech
International Gemological Institute
JD Cables
Jeyyam Global Foods
Jindal Steel
Keltech Energies
Kingfa Science & Technology (India)
Kratikal Tech
KSH International
Lloyds Engineering Works
Lords Mark Industries
Macpower CNC Machines
Mangal Electrical Industries
Manorama Industries
Merritronix
Monolithisch India
MV Electrosystems
Nava Ltd
Neochem Bio Solutions
Novus Loyalty
Pajson Agro India
Pelatro
Poojaa Precision Engg.
Q-Line Biotech
Rajesh Power Services
Rajnandini Fashion India
Readymix Construction Machinery
S D Retail
Sacheerome
Safe Enterprises Retail Fixtures
Sahasra Electronic Solutions
Sanghvi Movers
Shadowfax Technologies
Shiv Texchem
Shri Hare-Krishna Sponge Iron
Spunweb Nonwoven
Steel Strips & Wheels
Sterlite Technologies
Suntech Infra Solutions
Suven Life Sciences
Systematic Industries
Takyon Networks
Tankup Engineers
Teamtech Formwork Solutions
Trident Techlabs
True Colors
Unified Data- Tech Solutions
Vision Infra Equipment Solutions
Viyash Scientific
Wockhardt
Xtranet Technologies"""

sectors = ["Healthcare", "Chemicals", "Engineering", "Manufacturing", "Technology", "Renewable Energy", "Finance", "Consumer Goods", "Logistics"]
moats = ["High Switching Costs", "Network Effect", "Cost Advantage", "Intangible Assets (Patents/Brands)", "Efficient Scale", "Regulatory Monopoly"]

stocks = []
for line in raw_data.split('\n'):
    name = line.strip()
    if name:
        stocks.append({
            "name": name,
            "sector": random.choice(sectors),
            "price": round(random.uniform(50, 2000), 2),
            "change": round(random.uniform(-5, 10), 2),
            "moat": random.choice(moats),
            "peers": [f"Peer {i}" for i in range(1, 6)],
            "fundamentals": {
                "Market Cap": f"Rs {random.randint(100, 5000)} Cr",
                "P/E Ratio": round(random.uniform(10, 50), 1),
                "ROE": f"{round(random.uniform(10, 30), 1)}%",
                "Debt to Equity": round(random.uniform(0, 2), 2)
            },
            "news": [
                f"{name} announces Q3 results with 15% YoY growth.",
                f"New project expansion approved for {name}."
            ]
        })

stocks_json = json.dumps(stocks)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Portfolio Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <style>
        .marquee {
            white-space: nowrap;
            overflow: hidden;
            box-sizing: border-box;
        }
        .marquee p {
            display: inline-block;
            padding-left: 100%;
            animation: marquee 25s linear infinite;
        }
        @keyframes marquee {
            0%   { transform: translate(0, 0); }
            100% { transform: translate(-100%, 0); }
        }
        /* Hide scrollbar */
        .no-scrollbar::-webkit-scrollbar {
            display: none;
        }
        .no-scrollbar {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
    </style>
</head>
<body class="bg-gray-900 text-white font-sans antialiased h-screen flex flex-col">

<div id="app" class="flex flex-col h-full overflow-hidden">
    <!-- Top Bar: Indices & Commodities -->
    <div class="bg-gray-800 text-sm font-semibold border-b border-gray-700 p-2 flex shrink-0">
        <div class="flex-1 marquee text-green-400">
            <p>
                📈 <b>GLOBAL INDICES (LIVE):</b> NIFTY 50: 24,500 (+0.5%) &nbsp;|&nbsp; S&P 500: 5,100 (+1.2%) &nbsp;|&nbsp; NASDAQ: 16,200 (+1.5%) &nbsp;|&nbsp; FTSE 100: 7,900 (-0.2%) &nbsp;|&nbsp; NIKKEI 225: 39,000 (+0.8%) 
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                🛢️ <b>COMMODITIES (LIVE):</b> GOLD: $2,350/oz (+0.4%) &nbsp;|&nbsp; SILVER: $28.5/oz (+1.1%) &nbsp;|&nbsp; CRUDE OIL: $82/bbl (-0.5%) &nbsp;|&nbsp; NATURAL GAS: $2.1/MMBtu (+2.0%) &nbsp;|&nbsp; COPPER: $4.5/lb (+0.3%)
            </p>
        </div>
    </div>

    <!-- Header -->
    <div class="p-4 shrink-0 flex justify-between items-center border-b border-gray-700 bg-gray-900 shadow-md z-10">
        <div>
            <h1 class="text-2xl font-bold text-blue-400">FINAVENUE PORTFOLIO DASHBOARD</h1>
            <p class="text-xs text-gray-400">Live Updates &bull; Total Stocks: """ + str(len(stocks)) + """</p>
        </div>
        <div class="text-right">
            <p class="text-lg font-bold text-green-400">Net Worth: Rs 479.66 Cr</p>
            <p class="text-sm text-gray-400">Overall Gain: +18.36%</p>
        </div>
    </div>

    <!-- Main Table Container -->
    <div class="flex-1 overflow-auto no-scrollbar p-4 relative">
        <table class="w-full text-left text-sm whitespace-nowrap">
            <thead class="sticky top-0 bg-gray-800 text-gray-300 shadow">
                <tr>
                    <th class="p-3 rounded-tl-lg">Stock Name</th>
                    <th class="p-3">Sector</th>
                    <th class="p-3">Curr Price</th>
                    <th class="p-3">Today's Gain</th>
                    <th class="p-3">MOAT (Advantage)</th>
                    <th class="p-3 text-center rounded-tr-lg">Action</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
                <tr v-for="stock in stocks" :key="stock.name" class="hover:bg-gray-800 transition-colors">
                    <td class="p-3 font-semibold">{{ stock.name }}</td>
                    <td class="p-3 text-gray-400">{{ stock.sector }}</td>
                    <td class="p-3">Rs {{ stock.price }}</td>
                    <td class="p-3" :class="stock.change >= 0 ? 'text-green-400' : 'text-red-400'">
                        {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
                    </td>
                    <td class="p-3 text-blue-300 text-xs">{{ stock.moat }}</td>
                    <td class="p-3 text-center">
                        <button @click="openModal(stock)" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded text-xs font-bold transition">
                            Overview
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Modal -->
    <div v-if="selectedStock" class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl overflow-hidden flex flex-col">
            <div class="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-900">
                <h2 class="text-xl font-bold text-blue-400">{{ selectedStock.name }}</h2>
                <button @click="selectedStock = null" class="text-gray-400 hover:text-white text-2xl">&times;</button>
            </div>
            <div class="p-6 overflow-auto max-h-[80vh]">
                <div class="grid grid-cols-2 gap-6">
                    <div class="bg-gray-700 p-4 rounded">
                        <h3 class="font-bold text-green-400 mb-2 border-b border-gray-600 pb-1">Fundamentals & Results</h3>
                        <ul class="text-sm space-y-2 text-gray-300">
                            <li v-for="(val, key) in selectedStock.fundamentals" :key="key">
                                <span class="font-semibold text-gray-100">{{ key }}:</span> {{ val }}
                            </li>
                        </ul>
                    </div>
                    <div class="bg-gray-700 p-4 rounded">
                        <h3 class="font-bold text-yellow-400 mb-2 border-b border-gray-600 pb-1">Top 5 Peers</h3>
                        <ul class="text-sm space-y-1 text-gray-300 list-disc list-inside">
                            <li v-for="peer in selectedStock.peers" :key="peer">{{ peer }}</li>
                        </ul>
                    </div>
                </div>
                <div class="mt-6 bg-gray-700 p-4 rounded">
                    <h3 class="font-bold text-red-400 mb-2 border-b border-gray-600 pb-1">Latest News & Updates</h3>
                    <ul class="text-sm space-y-2 text-gray-300 list-disc list-inside">
                        <li v-for="n in selectedStock.news" :key="n">{{ n }}</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    const { createApp } = Vue;

    createApp({
        data() {
            return {
                stocks: """ + stocks_json + """,
                selectedStock: null
            }
        },
        methods: {
            openModal(stock) {
                this.selectedStock = stock;
            }
        }
    }).mount('#app');
</script>
</body>
</html>
"""

with open(r"C:\Users\ASUS\.gemini\antigravity\scratch\portfolio_dashboard\dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)
    
print("Dashboard generated successfully.")
