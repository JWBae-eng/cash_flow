Personal Cash Flow Visualizer

A local Python application that transforms raw transaction data from Empower (Personal Capital) into interactive financial dashboards.

Built with Streamlit and Plotly, this tool runs entirely on your own machine. Your financial data never leaves your computer.

🛠 Installation
Prerequisites
Python 3.8+ installed on your system.

1. Clone or Save the Project
Create a folder for your project (e.g., cash_flow_app) and save the application code as app.py.

2. Install Dependencies
Open your terminal or command prompt and run the following command to install the required libraries:

Bash
pip install streamlit pandas plotly
streamlit: The framework that turns the Python script into a web app.

pandas: For efficient data processing and cleaning.

plotly: For generating interactive charts.

If use conda or mamba
conda create -n cash_flow python streamlit pandas plotly
conda activate cash_flow

Tip: use your own environment name "cash_flow"

🚀 How to Use
1. Export Your Data
Log in to your Empower Personal Dashboard.

Navigate to Banking > Cash Flow.

Click the CSV icon (usually top-right of the transaction list) to download your transactions.csv file.

2. Run the App
Navigate to your project folder in the terminal and run:

Bash
streamlit run app.py
This will automatically open a new tab in your default web browser (usually at http://localhost:8501).

3. Analyze Your Finances
Upload: Drag and drop your transactions.csv file into the file uploader area.

Filter: Use the sidebar to select specific accounts (e.g., exclude "Investment" accounts if needed).

Clean: Toggle "Enable Transfer Cleaning" in the sidebar. This effectively removes:

Outflows labeled "Online Services" (Credit Card Payments).

Inflows labeled "Refunds & Reimbursements" (Payment Received).

Note: It only removes them if they are an exact dollar match, preserving legitimate refunds.

Explore: Switch between the tabs (Category, Merchant, Trend) to visualize your spending habits.
