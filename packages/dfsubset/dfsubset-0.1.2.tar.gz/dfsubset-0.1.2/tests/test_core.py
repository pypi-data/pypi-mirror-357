import pandas as pd
from dfsubset import subset

def test_subset_basic():
    df = pd.DataFrame({
        'name': ['Ali', 'sambili', 'Ciku'],
        'score': [75, 82, 68]
    })
    result = subset(df, 'score > 70', select='name')
    assert result.shape == (2, 1)
    assert 'Ali' in result['name'].values