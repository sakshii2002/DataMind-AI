import pandas as pd
import numpy as np
import streamlit as st

def analyze_data_quality(df: pd.DataFrame) -> dict:
    report = {}

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    report["missing"] = pd.DataFrame({
        "Column": missing.index,
        "Missing Count": missing.values,
        "Missing %": missing_pct.values
    }).query("`Missing Count` > 0").reset_index(drop=True)

    # Duplicates
    report["duplicate_rows"] = df.duplicated().sum()
    report["duplicate_pct"] = round(report["duplicate_rows"] / len(df) * 100, 2)

    # Data types
    report["dtypes"] = df.dtypes.reset_index()
    report["dtypes"].columns = ["Column", "Type"]

    # Outliers (IQR method for numeric)
    numeric_cols = df.select_dtypes(include="number").columns
    outlier_info = []
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        n_outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        if n_outliers > 0:
            outlier_info.append({
                "Column": col,
                "Outlier Count": n_outliers,
                "Outlier %": round(n_outliers / len(df) * 100, 2),
                "Lower Bound": round(lower, 3),
                "Upper Bound": round(upper, 3)
            })
    report["outliers"] = pd.DataFrame(outlier_info)

    # Unique values for categorical
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    cat_info = []
    for col in cat_cols:
        cat_info.append({
            "Column": col,
            "Unique Values": df[col].nunique(),
            "Top Value": df[col].mode()[0] if not df[col].mode().empty else "N/A",
            "Top Freq %": round(df[col].value_counts().iloc[0] / len(df) * 100, 1) if not df[col].empty else 0
        })
    report["categorical"] = pd.DataFrame(cat_info)

    # Overall score
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    dup_rows = report["duplicate_rows"]
    n_outliers_total = sum(r["Outlier Count"] for r in outlier_info)
    issues = missing_cells + dup_rows + n_outliers_total
    score = max(0, round(100 - (issues / max(total_cells, 1) * 100), 1))
    report["quality_score"] = score

    return report

def clean_data(df: pd.DataFrame, options: dict) -> pd.DataFrame:
    cleaned = df.copy()
    log = []

    if options.get("drop_duplicates"):
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        dropped = before - len(cleaned)
        if dropped:
            log.append(f"✅ Removed {dropped} duplicate rows")

    if options.get("fill_numeric"):
        num_cols = cleaned.select_dtypes(include="number").columns
        for col in num_cols:
            n = int(cleaned[col].isnull().sum())
            if n > 0:
                med = cleaned[col].median()
                if not pd.isna(med):
                    cleaned[col] = cleaned[col].fillna(med)
                    log.append(f"✨ Filled {n} missing values in `{col}` with median ({med})")

    if options.get("fill_categorical"):
        cat_cols = cleaned.select_dtypes(include=["object", "category"]).columns
        for col in cat_cols:
            n = int(cleaned[col].isnull().sum())
            if n > 0:
                mode_res = cleaned[col].mode()
                if not mode_res.empty:
                    val = mode_res[0]
                    cleaned[col] = cleaned[col].fillna(val)
                    log.append(f"✨ Filled {n} missing values in `{col}` with mode ('{val}')")

    if options.get("drop_missing_rows"):
        before = len(cleaned)
        cleaned = cleaned.dropna()
        dropped = before - len(cleaned)
        if dropped:
            log.append(f"✅ Dropped {dropped} rows with any missing values")

    return cleaned, log
