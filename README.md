# MASS — Research Studio

MASS is a Streamlit research assistant that searches the web, reads a relevant source, writes a structured report, and provides a critique. Reports can be downloaded as Markdown.

## Setup

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:

   ```text
   GOOGLE_API_KEY=your_google_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

## Run

```powershell
streamlit run app.py
```

Enter a research topic in the app to generate a report and review.
