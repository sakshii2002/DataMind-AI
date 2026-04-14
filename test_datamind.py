import pandas as pd
import pytest
import io
import numpy as np
from utils.data_quality import clean_data, analyze_data_quality

def test_data_quality_analysis():
    # Create sample dirty data
    df = pd.DataFrame({
        'A': [1.0, 2.0, np.nan, 4.0, 1.0],
        'B': ['x', 'y', 'z', 'x', 'x'],
        'C': [10.0, 20.0, 30.0, 40.0, 500.0] # 500 is an outlier
    })
    
    report = analyze_data_quality(df)
    
    assert report['quality_score'] < 100
    assert report['duplicate_rows'] == 0 # (1, 'x', 500) vs (1, 'x', 10) are different
    assert not report['missing'].empty
    assert len(report['outliers']) > 0

def test_data_cleaning():
    df = pd.DataFrame({
        'A': [1, 2, None, 4, 1],
        'B': ['x', 'y', None, 'x', 'x'],
        'C': [1, 1, 1, 1, 1] 
    })
    # Add a duplicate row
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    
    options = {
        "drop_duplicates": True,
        "fill_numeric": True,
        "fill_categorical": True,
        "drop_missing_rows": False
    }
    
    cleaned, log = clean_data(df, options)
    
    # Verify duplicates removed (Row 0, 4, and 5 are identical, should leave only 1)
    # Unique rows: (1,x,1), (2,y,1), (None,None,1), (4,x,1) -> Total 4
    assert len(cleaned) == 4
    # Verify nulls filled
    assert cleaned['A'].isnull().sum() == 0
    assert cleaned['B'].isnull().sum() == 0
    # Verify log messages
    assert any("Removed 2 duplicate rows" in m for m in log)
    assert any("Filled 1 missing values" in m for m in log)

def test_google_sheet_regex():
    import re
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0"
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    assert match is not None
    assert match.group(1) == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    gid_match = re.search(r"gid=(\d+)", url)
    assert gid_match.group(1) == "0"
