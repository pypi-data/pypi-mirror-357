# dfsubset

A simple R-style subset function for pandas DataFrames.

## Usage
```python
from dfsubset import subset
subset(df, 'score > 70', select='name')
```