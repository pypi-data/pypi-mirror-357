# dfsubset

A simple, readable `subset()` function for pandas DataFrames — inspired by R.

## Install
```bash
pip install dfsubset
```

## Usage
```python
from dfsubset import subset
import pandas as pd

df = pd.DataFrame({
    'name': ['Ali', 'Bora', 'Ciku'],
    'score': [75, 82, 68],
    'height': [160, 170, 165]
})

# Filter and select
subset(df, 'score > 70', select='name')

# Rename columns while selecting
subset(df, 'score > 70', select={'name': 'student', 'score': 'mark'})

# Save filtered data to a CSV
subset(df, 'score > 70', save_as='passed.csv')

# Get summary stats
subset(df, summarize='score')

# Multiple summaries
subset(df, summarize=['score', 'height'])
```