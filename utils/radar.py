import json
import pandas as pd
from utils.ai import _generate_with_retry, build_data_context
from google.genai import types

def scan_for_anomalies(df: pd.DataFrame):
    """
    Scans the dataset for behavioral red flags and hidden patterns using AI.
    Returns a list of finding dictionaries.
    """
    if df is None or df.empty:
        return []

    data_ctx = build_data_context(df)
    stats_ctx = df.describe(include='all').to_string()

    system_prompt = (
        "You are the DataMind Anomaly Radar, a proactive data monitoring agent.\n"
        "Your task is to analyze the statistical summary and sample of a dataset to find 3-5 "
        "hidden 'behavioral' anomalies or interesting red flags that a human might miss.\n\n"
        "Rules:\n"
        "1. Focus on outliers, weird correlations, or suspicious distributions.\n"
        "2. Provide a 'Severity' level: High (Red), Medium (Orange), Low (Yellow).\n"
        "3. Respond ONLY with a valid JSON list of objects.\n\n"
        "JSON Format Example:\n"
        "[\n"
        "  {\n"
        "    \"title\": \"Extreme Revenue Outlier\",\n"
        "    \"description\": \"Region X shows 500% higher sales than average, suggesting possible data entry error or a massive win.\",\n"
        "    \"severity\": \"High\",\n"
        "    \"impact\": \"Revenue metrics might be skewed.\",\n"
        "    \"action\": \"Verify the raw records for Region X.\"\n"
        "  }\n"
        "]"
    )

    prompt = (
        f"Data Context:\n{data_ctx}\n\n"
        f"Statistical Summary:\n{stats_ctx}\n\n"
        "Identify the top 3-5 anomalies and respond with the JSON list."
    )

    try:
        response = _generate_with_retry(
            model_name="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
            )
        )
        
        # Clean the response text
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"Radar Error: {e}")
        return [
            {
                "title": "Radar Analysis Interrupted",
                "description": f"The anomaly radar encountered an error during scanning: {str(e)}",
                "severity": "Low",
                "impact": "No anomalies detected this turn.",
                "action": "Try refreshing the radar scan."
            }
        ]
