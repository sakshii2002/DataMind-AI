import json
import pandas as pd
from utils.ai import _generate_with_retry, build_data_context
from google.genai import types

def generate_data_story(df: pd.DataFrame):
    """
    Generates a narrative story from the dataset using AI.
    """
    if df is None or df.empty:
        return "No data to tell a story about."

    data_ctx = build_data_context(df)
    stats_ctx = df.describe(include='all').to_string()

    system_prompt = (
        "You are the DataMind AI Storyteller.\n"
        "Your goal is to transform raw numbers into a compelling, human-readable narrative.\n"
        "Do not just list stats; explain the 'So What?' and the business implications.\n\n"
        "Structure your response with these exact headers:\n"
        "### 📖 Chapter 1: The Setting (Introduction)\n"
        "### 🚀 Chapter 2: The Main Characters (Key Variables & Findings)\n"
        "### 📈 Chapter 3: The Plot Twist (Anomalies & Unexpected Trends)\n"
        "### 💡 Chapter 4: The Moral of the Story (Final Conclusions & Strategic Advice)\n\n"
        "Style: Professional, engaging, and highly insightful. Use emoji bullet points."
    )

    prompt = (
        f"Data Context:\n{data_ctx}\n\n"
        f"Statistical Summary:\n{stats_ctx}\n\n"
        "Write the full Data Story now."
    )

    try:
        response = _generate_with_retry(
            model_name="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.8,
            )
        )
        return response.text
    except Exception as e:
        return f"⚠️ **Storyteller Error:** Could not generate the story at this time. ({str(e)})"
