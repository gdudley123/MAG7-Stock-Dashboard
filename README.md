# MAG7-Stock-Dashboard
MAG7 Stock Dashboard
A real-time stock analysis and portfolio tracking web application focused on the MAG7 stocks: Apple, Tesla, Amazon, Microsoft, Meta, Google, and NVIDIA. This dashboard offers interactive charts, technical indicators, portfolio management, and risk metric calculations using data from the Alpha Vantage API.
Features
Stock Analyzer
•	Select from 7 top MAG7 stocks
•	Choose time ranges: 1M, 3M, 6M, 1Y, or Max
•	Visualize:
o	Candlestick charts
o	Moving Averages (MA20 & MA50) with volume
o	RSI (Relative Strength Index)
•	Auto-generated trading signals (Buy, Sell, Hold) based on MA and RSI
•	Risk metrics:
o	Average Annual Return
o	Annualized Volatility
o	Sharpe Ratio
o	Max Drawdown
Portfolio Tracker
•	Manually input your stock positions
•	Track:
o	Purchase vs. Current Price
o	P/L ($ and %)
o	Allocation breakdown (Pie chart)
•	Export portfolio as CSV

Setup Instructions
1. Clone the Repository
git clone https://github.com/yourusername/mag7-stock-dashboard.git cd mag7-stock-dashboard


2. Create and Activate a Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Requirements
pip install -r requirements.txt

4. Add Alpha Vantage API Key
API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"

5. Run the App
streamlit run stock_dashboardPRESENT.py

Dependencies
•	streamlit
•	pandas, numpy
•	matplotlib, mplfinance
•	alpha_vantage
You can install them all with:
pip install streamlit pandas numpy matplotlib mplfinance alpha_vantage
![image](https://github.com/user-attachments/assets/36387e09-3453-49f1-a941-e40ffe3fa6e9)
