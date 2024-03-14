import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates
from datetime import datetime, timedelta

plt.switch_backend('Agg')

def fetch_price_history(tag):
    current_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=18)).strftime('%Y-%m-%d')
    
    url = f"http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{tag}/columns?from={start_date}&till={current_date}&iss.meta=off&history.columns=CLOSE,TRADEDATE"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Error fetching price history")
        return None

def parse_price_history(price_history_xml):
    root = ET.fromstring(price_history_xml)
    prices = []
    dates = []
    rows = root.findall('.//row')
    rows = rows[-14:]
    for row in rows:
        price = row.get('CLOSE')
        date_str = row.get('TRADEDATE')
        if price and date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            prices.append(float(price))
            dates.append(date)
    return dates, prices

def plot_price_history(dates, prices):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, prices)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('Price History')
    ax.grid(True)

    min_price = min(prices) - (max(prices) - min(prices)) * 0.1
    max_price = max(prices) + (max(prices) - min(prices)) * 0.1
    ax.set_ylim(min_price, max_price)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    plt.close(fig)
    
    return image_base64
