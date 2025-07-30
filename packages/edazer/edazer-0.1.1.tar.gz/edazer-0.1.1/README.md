# Edazer

**Edazer** is a lightweight package that provides functionalities for common EDA tasks. It helps you quickly understand, summarize, and inspect your datasets with minimal code.

---

## Features

- **Quick DataFrame Summaries:** Instantly view info, describe, nulls, duplicates, and shape using `summary` method
- **Unique Value Inspection:** Easily display unique values for any or all columns.
- **Type-based Column Selection:** Find columns by dtype (e.g., numeric, categorical).
- **Flexible Subsetting:** Use the `lookup` method to view head, tail, or random samples.
- **Custom DataFrame Naming:** Track multiple DataFrames with custom names for clarity.

---

## Installation

```bash
pip install edazer
```

---

## Quick Start with Titanic Dataset

```python
import seaborn as sns
from edazer import Edazer

# Load the Titanic dataset from seaborn
titanic = sns.load_dataset('titanic')

# Create an Edazer instance
titanic_eda = Edazer(titanic, name="titanic") # setting name useful when working with multiple dataframes

#Complete DataFrame summary: info | descriptive statistics | nulls| duplicates | uniques | shape
titanic_eda.summarize_df()

# Show unique values for selected columns
titanic_eda.show_unique_values(column_names=['class', 'embarked'], max_unique=5)

# Get columns with float dtype
print(titanic_eda.cols_with_dtype(['float']))

#Combine multiple methods
titanic_dz.show_unique_values(column_names=titanic_dz.cols_with_dtype(dtypes=["object"]))

# Display the first few rows
print(titanic_eda.lookup("head"))

```

---

## API Reference

### `Edazer(df: pd.DataFrame, name: str = None)`

- **df:** The pandas DataFrame to analyze.
- **name:** Optional name for the DataFrame (useful when working with many DataFrames).

#### Methods

- `summarize_df()`: Print a summary (info, describe, nulls, duplicates, shape).
- `show_unique_values(column_names=None, max_unique=10)`: Show unique values for specified columns.
- `cols_with_dtype(dtypes)`: Return columns matching the given dtypes.
- `lookup(option="head")`: Return a subset of the DataFrame (`head`, `tail`, or `sample`).

---

## Example Output

```python
titanic_eda.show_unique_values(column_names=titanic_dz.cols_with_dtype(dtypes=["object"]))

# Output:
sex: ['male', 'female']
embarked: ['S', 'C', 'Q', nan]
who: ['man', 'woman', 'child']
embark_town: ['Southampton', 'Cherbourg', 'Queenstown', nan]
alive: ['no', 'yes']
```

---

## Contributing

Contributions are welcome! Please open issues or pull requests on Github
---

## License

MIT License

---

## Author
[adarsh3690704](https://github.com/adarsh-79)