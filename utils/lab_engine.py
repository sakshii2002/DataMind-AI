import streamlit as st
import pandas as pd
import re
from utils.ai import _generate_with_retry
from google.genai import types

def generate_transformation_code(user_request: str, df: pd.DataFrame) -> str:
    """Uses Gemini to translate an English request into a single pandas transformation block."""
    cols = list(df.columns)
    sample_data = df.head(3).to_string()
    
    system_prompt = (
        "You are a Senior Pandas Expert.\n"
        "Your goal is to generate Python code to transform a dataframe named 'df'.\n"
        "Rules:\n"
        "1. Write ONLY the code, no explanation, no markdown blocks. Just raw Python code.\n"
        "2. The dataframe is always named 'df'.\n"
        "3. Focus on single-block transformations (creating columns, filtering, aggregating).\n"
        "4. DO NOT include any imports or print statements.\n"
        "5. Ensure the code is robust and handles potential missing data if possible.\n"
    )
    
    prompt = (
        f"Available columns: {cols}\n"
        f"Sample data preview:\n{sample_data}\n\n"
        f"User Instruction: {user_request}\n\n"
        "Generate the pandas code for this transformation:"
    )

    try:
        response = _generate_with_retry(
            model_name="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1
            )
        )
        
        # Clean the code (remove potential markdown markers if AI ignores instructions)
        code = response.text.strip()
        code = re.sub(r'```python\n?', '', code)
        code = re.sub(r'```', '', code)
        return code.strip()
    except Exception as e:
        st.error(f"AI Transformation Error: {e}")
        return ""

def apply_safe_transformation(df: pd.DataFrame, code: str):
    """Executes the generated code on a copy of the dataframe and returns the result."""
    if not code:
        return df, "No code generated."
    
    # 1. Basic safety check: check for dangerous keywords
    dangerous_keywords = ['import ', 'os.', 'sys.', 'shutil.', 'open(', 'subprocess', 'requests.', 'socket', 'pickle']
    if any(k in code for k in dangerous_keywords):
        return df, "Blocked potentially unsafe code."

    # 2. Local context for exec
    local_vars = {'df': df.copy(), 'pd': pd}
    
    try:
        # 3. Execution (The code should modify local_vars['df'])
        exec(code, {}, local_vars)
        new_df = local_vars['df']
        
        # 4. Check if it's still a dataframe
        if not isinstance(new_df, pd.DataFrame):
            return df, f"Transformation result was not a table. Model produced: {type(new_df)}"
            
        summary = f"Applied transformation:\n`{code}`"
        return new_df, summary
        
    except Exception as e:
        return df, f"Runtime Error while applying transformation: {e}\nGenerated Code: `{code}`"
