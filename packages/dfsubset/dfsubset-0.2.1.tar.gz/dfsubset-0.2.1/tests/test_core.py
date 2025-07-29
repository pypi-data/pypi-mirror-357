import pandas as pd
from dfsubset import subset

def test_summary():
    df = pd.DataFrame({
        'score': [75, 82, 68],
        'height': [160, 170, 165]
    })
    result = subset(df, summarize=['score', 'height'])
    assert 'mean' in result.columns
    assert 'score' in result.index
    assert 'height' in result.index