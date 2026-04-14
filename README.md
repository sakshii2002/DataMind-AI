# 🧠 DataMind AI — Intelligent Data Analysis Agent

A full-featured AI-powered data analysis agent built with **Streamlit** and **Google Gemini**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **AI Chat** | Ask questions about your data in plain English |
| 📊 **Smart Charts** | AI-generated or manual chart builder with PNG/SVG download |
| 🔍 **Data Quality** | Detect missing values, duplicates, outliers + one-click cleaning |
| 📋 **Dashboard** | Auto-generated analytics overview with AI insights |
| 🔮 **Predictions** | Time-series forecasting & regression models (Linear, RF, GBM) |
| 📄 **PDF Report** | Full downloadable report with charts, stats & AI insights |
| 🌙 **Dark/Light Mode** | Toggle from sidebar, applies globally |
| 📂 **CSV & PDF Upload** | Supports both file types |

---

## 🚀 Quick Start

### 1. Clone / download the project

```bash
cd data_agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Edit `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```

Get a free API key at: https://aistudio.google.com/app/apikey

Or set it as an environment variable:

```bash
export GEMINI_API_KEY="your-key-here"      # Mac/Linux
set GEMINI_API_KEY=your-key-here           # Windows
```

### 5. Run the app

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📁 Project Structure

```
data_agent/
├── app.py                        # Main entry point
├── requirements.txt
├── .streamlit/
│   ├── config.toml               # Streamlit theme config
│   └── secrets.toml              # API keys (don't commit this!)
├── components/
│   ├── sidebar.py                # Sidebar: upload, nav, dark mode
│   ├── main_view.py              # Tab router
│   ├── chat_tab.py               # AI chat interface
│   ├── charts_tab.py             # Chart builder (AI + manual + auto)
│   ├── quality_tab.py            # Data quality analysis & cleaning
│   ├── dashboard_tab.py          # Analytics dashboard
│   ├── predictions_tab.py        # ML forecasting & regression
│   └── download_tab.py           # PDF/CSV/chart downloads
└── utils/
    ├── state.py                  # Session state initialization
    ├── styles.py                 # CSS injection (dark/light mode)
    ├── ai.py                     # Gemini API integration
    ├── charts.py                 # Plotly chart builders
    ├── data_quality.py           # Quality analysis & cleaning
    └── report.py                 # PDF report generation (reportlab)
```

---

## 🗝️ API Key Setup

The agent uses **Google Gemini 1.5 Flash** (free tier available).

1. Go to https://aistudio.google.com/app/apikey
2. Create a new API key
3. Paste it into `.streamlit/secrets.toml`

---

## 📦 Dependencies

- `streamlit` — Web UI framework
- `google-generativeai` — Gemini AI integration
- `pandas` / `numpy` — Data processing
- `plotly` — Interactive charts
- `kaleido` — Chart image export (PNG/SVG)
- `reportlab` — PDF report generation
- `pdfplumber` — PDF data extraction
- `scikit-learn` — ML predictions

---

## 💡 Usage Tips

- Upload a CSV from the **sidebar** to start
- Use the **Chat** tab for natural language queries
- Run **Data Quality** before any analysis
- Use **AI Chart** in the Charts tab — just describe what you want
- Generate the **PDF Report** from the Download tab for sharing
- Toggle **Dark Mode** from the sidebar

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `GEMINI_API_KEY not set` | Add key to `.streamlit/secrets.toml` |
| Chart download not working | `pip install kaleido` |
| PDF generation fails | `pip install reportlab` |
| PDF table extraction fails | `pip install pdfplumber` |
| Slow on large files | Filter to <50K rows before uploading |
