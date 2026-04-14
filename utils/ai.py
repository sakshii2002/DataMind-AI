import os
import json
import streamlit as st
from google import genai
from google.genai import types


# ── API client ───────────────────────────────────────────────────────────────

def _get_client() -> genai.Client:
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not set. Add it to `.streamlit/secrets.toml` or env vars.")
        st.stop()
    return genai.Client(api_key=api_key)

def _generate_with_retry(model_name: str, contents, config=None, max_retries=3, wait_time=5.0):
    """Safety wrapper to handle quota/429 errors with automatic retries."""
    import time
    client = _get_client()
    
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            last_error = e
            error_str = str(e).upper()
            # Handle Quota (429) and High Demand (503)
            if any(code in error_str for code in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "QUOTA"]):
                if attempt < max_retries - 1:
                    time.sleep(wait_time * (attempt + 1))
                    continue
            raise e
    raise last_error

# ── Data context builder ──────────────────────────────────────────────────────

def build_data_context(df) -> str:
    if df is None:
        return ""
    sample   = df.head(5).to_string()
    dtypes   = df.dtypes.to_string()
    shape    = df.shape
    cols     = list(df.columns)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    return (
        f"Dataset Info:\n"
        f"- Shape: {shape[0]} rows x {shape[1]} columns\n"
        f"- Columns: {cols}\n"
        f"- Numeric columns: {num_cols}\n"
        f"- Dtypes:\n{dtypes}\n"
        f"- Sample (first 5 rows):\n{sample}\n"
    )


# ── Chat with data ────────────────────────────────────────────────────────────

def chat_with_data(user_msg: str, df, history: list) -> str:
    try:
        client   = _get_client()
        data_ctx = build_data_context(df)

        system_prompt = (
            "You are DataMind AI, an expert data analyst assistant.\n"
            "You help users understand, analyze, and visualize their data.\n"
            "Be concise, insightful, and friendly. Use bullet points for clarity.\n"
            "When suggesting charts or analysis steps, be specific.\n\n"
            "Current dataset context:\n"
            + (data_ctx if data_ctx else "No data uploaded yet.")
            + "\n\nWhen users ask to create charts, describe what chart type and columns to use "
              "in a structured way.\nWhen users ask about data quality, summarize key findings.\n"
        )

        # Build conversation history (last 10 turns)
        contents = []
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part(text=user_msg)]))

        response = _generate_with_retry(
            model_name="gemini-flash-latest",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            ),
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "⚠️ **Quota reached.** The AI model is currently at its free tier limit. Please wait about 15-30 seconds and try again."
        return f"⚠️ **AI Error:** {error_msg}"


# ── Chart config generator ────────────────────────────────────────────────────

def generate_chart_config(user_request: str, df) -> dict:
    try:
        client    = _get_client()
        cols      = list(df.columns) if df is not None else []
        num_cols  = df.select_dtypes(include="number").columns.tolist() if df is not None else []
        cat_cols  = df.select_dtypes(include=["object", "category"]).columns.tolist() if df is not None else []

        prompt = (
            f'Given this user request: "{user_request}"\n'
            f"Available columns: {cols}\n"
            f"Numeric columns: {num_cols}\n"
            f"Categorical columns: {cat_cols}\n\n"
            "Respond with ONLY valid JSON (no markdown, no explanation) like this:\n"
            '{\n'
            '  "chart_type": "bar|line|scatter|pie|histogram|box|heatmap",\n'
            '  "x": "column_name_or_null",\n'
            '  "y": "column_name_or_null",\n'
            '  "color": "column_name_or_null",\n'
            '  "title": "chart title",\n'
            '  "agg": "sum|mean|count|none"\n'
            "}\nPick the best columns for the request."
        )

        response = _generate_with_retry(
            model_name="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1),
        )
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(text)
        except Exception:
            # Fallback if AI output is malformed
            return {
                "chart_type": "bar",
                "x": cols[0] if cols else None,
                "y": num_cols[0] if num_cols else None,
                "color": None,
                "title": "Analysis Chart",
                "agg": "count",
            }
    except Exception:
        return None


# ── Vision: Chart to Code ───────────────────────────────────────────────────

def analyze_chart_image(image_bytes: bytes, df, user_prompt: str = None) -> dict:
    try:
        client = _get_client()
        cols = list(df.columns) if df is not None else []
        num_cols = df.select_dtypes(include="number").columns.tolist() if df is not None else []
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist() if df is not None else []

        system_prompt = (
            "You are a visual data analyst. You will be provided with an image of a chart and "
            "metadata about a dataset. Your task is to extract the chart's structure and map it "
            "to the available columns in the provided dataset to recreate it.\n\n"
            f"Available columns: {cols}\n"
            f"Numeric columns: {num_cols}\n"
            f"Categorical columns: {cat_cols}\n\n"
            "Respond with ONLY valid JSON (no markdown, no explanation):\n"
            '{\n'
            '  "chart_type": "bar|line|scatter|pie|histogram|box|heatmap",\n'
            '  "x": "column_name_or_null",\n'
            '  "y": "column_name_or_null",\n'
            '  "color": "column_name_or_null",\n'
            '  "title": "extracted or suggested title",\n'
            '  "agg": "sum|mean|count|none"\n'
            "}\n"
        )

        user_text = "Recreate this chart from the image using the data context provided."
        if user_prompt:
            user_text += f"\nSpecific user instructions: {user_prompt}"

        # Combine text and image parts
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=user_text),
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                ]
            )
        ]

        response = _generate_with_retry(
            model_name="gemini-flash-latest",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1
            ),
        )

        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"Vision error: {e}")
        return None


# ── Insights generator ────────────────────────────────────────────────────────

def generate_insights(df) -> str:
    try:
        client = _get_client()
        if df is None:
            return "No data loaded."
        ctx  = build_data_context(df)
        desc = df.describe().to_string() if not df.empty else ""
        prompt = (
            "Analyze this dataset and provide 5-7 key business insights, patterns, "
            "anomalies, and recommendations.\n"
            "Be specific and actionable. Use emoji bullets.\n\n"
            + ctx
            + "\n\nDescriptive stats:\n"
            + desc
        )
        response = _generate_with_retry(
            model_name="gemini-flash-latest",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "⚠️ **Quota limit reached.** Please wait a moment and try refreshing the insights."
        return f"⚠️ **AI Insight Error:** Could not generate insights at this time."