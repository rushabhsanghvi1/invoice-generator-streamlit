# GST Invoice & Annexure Generator

A web-based invoice generation application built with Streamlit that generates GST invoices and annexures as PDF files.

## 🚀 Live Demo
[Your Render URL will appear here after deployment]

## ✨ Features

- 📤 Upload Invoice and Orders CSV files
- 🏷️ Select invoice ID from dropdown menu
- 📄 Generate merged PDF (Invoice + Annexure)
- ⬇️ One-click PDF download
- 🧮 Automatic GST calculations (CGST, SGST)
- 📊 Real-time metrics display

## 📋 CSV Format Requirements

### Invoice CSV
- Invoice ID
- Order ID
- Invoice date
- ASIN
- SKU
- HSN
- Quantity
- Item Cost
- GST Rate

### Orders CSV
- Order ID
- Ship To Address Line 1
- Ship To Address Line 2
- Ship To Address Line 3
- Ship To City
- Ship To State
- Ship To ZIP Code

## 🛠️ Local Setup

1. Clone repository:
```bash
git clone https://github.com/YOUR_USERNAME/invoice-generator-streamlit.git
cd invoice-generator-streamlit
```

2. Create virtual environment:
```bash
python -m venv streamlit_env
streamlit_env\Scripts\activate  # Windows
source streamlit_env/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run application:
```bash
streamlit run app.py
```

5. Open browser to `http://localhost:8501`

## 📖 Usage

1. Click on sidebar to upload Invoice CSV
2. Click on sidebar to upload Orders CSV
3. Wait for success messages
4. Select Invoice ID from dropdown
5. (Optional) Check "Preview Data" to see invoice details
6. Click "Generate Merged PDF" button
7. Click "Download PDF" to save file

## 🌐 Technologies Used

- Python 3.9+
- Streamlit 1.28.1
- pandas 2.0.3
- fpdf2 2.7.0
- Pillow 10.0.0

## 📦 Deployment

Deployed on **Render.com** with automatic CI/CD from GitHub.

## 📝 License

MIT License

## 👨‍💼 Author

Jain Sanghvi & Co.