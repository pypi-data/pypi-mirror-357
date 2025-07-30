
#import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
from typing import List
#import duckdb
import warnings
from IPython import get_ipython

"""
- use in ipynb files as display() is involved
- few validation checks
"""

class Edazer: 
    """
    Exploratory data analyzer. Can be used to analyze multiple DataFrames separately,
    each as an instance of Edazer.

    Parameters
    ----------
    `df` : pd.DataFrame
        The DataFrame to analyze.
    `name` : str, optional
        Name of the DataFrame. If not provided, the analyzer will not display a name.
    """
    __shell = get_ipython().__class__.__name__ 
    if __shell != "ZMQInteractiveShell":
        warnings.warn("Some methods may work only in a Jupyter notebook", UserWarning)
    
    def __init__(self, df: pd.DataFrame, name: str=None): 
        self.df = df

        self.__df_name = None
        if name is not None:
            self.__df_name = name

    def __repr__(self):
        if self.__df_name is not None:
            return f"Analyzer for the DataFrame: {self.__df_name}"
        else:
            return super().__repr__()

    def lookup(self,option: str= "head") -> pd.DataFrame:
        """
        Return a subset of the DataFrame.

        Parameters
        ----------
        `option`: str, optional 
        The option to choose. Defaults to "head".

        Options:
        ----------
        - 'head': Return the first few rows of the DataFrame.
        - 'tail': Return the last few rows of the DataFrame.
        - 'sample': Return a random sample of rows from the DataFrame.

        Returns
        -------
        pd.DataFrame
            The selected subset of the DataFrame.
        """
        
        option = option.lower()
        if (option == "head"):
            display(self.df.head())
        elif option == "tail":
            display(self.df.tail())
        elif option == "sample":
            display(self.df.sample())    
        else: 
            raise ValueError("Invalid option. Valid options are: head, tail, sample")    

    def summarize_df(self):
        """
        Summarizes the DataFrame by providing information about its 
        shape, null values, duplicated rows, unique values, and descriptive statistics.

        The following information is provided:
        - DataFrame info
        - Descriptive statistics (mean, std, min, 25%, 50%, 75%, 99%)
        - Number of null values
        - Number of duplicated rows
        - Number of unique values
        - DataFrame shape (number of rows and columns)
        """
        
        print("DataFrame Info:")
        print("-"*25) 
        display(self.df.info()) 
        print("\n")

        print("DataFrame Description:")
        print("-"*25) 
        display(self.df.describe(percentiles=[.25, .50, .75, .99]).T)
        print("\n")

        print("Number of Null Values:")
        print("-"*25) 
        display(self.df.isnull().sum()) 
        print("\n")

        print("Number of Duplicated Rows:")
        print("-"*25)
        display(int(self.df.duplicated().sum())) 
        print("\n")

        print("Number of Unique Values:")
        print("-"*25)
        display(self.df.nunique()) 
        print("\n")

        print("DataFrame Shape:")
        print("-"*25)
        print(f"No. of Rows:    {self.df.shape[0]}\nNo. of Columns: {self.df.shape[1]}")

    def show_unique_values(self, column_names: List[str]=None, max_unique: int=10):
        """
        Displays the unique values for each column.
                
        Parameters
        ----------
        `column_names` : List[str], optional
            List of column names to display unique values for.\n
            If None, defaults to columns with dtype: category, object.
        `max_unique` : int, optional
            The maximum number of unique values to display. Defaults to 10.

        Notes
        -----
        For numeric columns, pass in the column names through `column_names` or pass all column names.\n
        If all columns have more than `max_unique` unique values, a message will be printed suggesting 
        to set a higher `max_unique` value.
        """
        if not isinstance(max_unique, int):
            raise TypeError("'max_unique' must be an integer.")
        if column_names is None:
            column_names= self.df.select_dtypes(include=["category", "object"]).columns
        
        less_than_max_unique_cols = []
        for col in column_names:
            if self.df[col].nunique() <= max_unique:
                print(f"{col}: {list(self.df[col].unique())}")
                #print("\n")
            else:
                less_than_max_unique_cols.append(col)

        n_less_than_max_unique_cols =  len(less_than_max_unique_cols)

        if  n_less_than_max_unique_cols == len(column_names): 
            print(f"All the mentioned columns have more than {max_unique} unique values")
        elif n_less_than_max_unique_cols > 0 :
            print(f"\n{less_than_max_unique_cols} have more than {max_unique} unique values. Set it to a higher Value")
        

    def cols_with_dtype(self, dtypes: List[str], exact: bool= False):
        """
        Returns the column names of the DataFrame with the specified data types.
        
        Parameters
        ----------
        `dtypes` (List[str]): A list of data types to match.

        `exact` (bool, optional): If True, only exact matches are returned. If False, matches are made by removing numeric characters from the data type names. 
        Defaults to False.\n
        For example
            - If `exact=True`, 'int64' will only match columns with exact data type 'int64'.\n
            - If `exact=False`, 'int' will match columns with data types 'int64', 'int32', etc.\n
            - If `exact=False`, 'float' will match columns with data types 'float64', 'float32', etc.\n
            - If `exact=True` or `exact=False`, 'object' will match columns with data type 'object'.
        
        Notes
        --------
        Useful while plotting bar plot, count plot, histplot etc ...
        """

        if (not isinstance(dtypes, list)) or (not all(isinstance(x, str) for x in dtypes)):
            raise TypeError("dtypes must be a list of strings")

        if not exact:
            remove_num_from_str = lambda s: ''.join([char for char in str(s) if char.isalpha()])
            dtype_without_nums = self.df.dtypes.apply(remove_num_from_str)
            return self.df.columns[dtype_without_nums.isin(dtypes)]
        
        return self.df.columns[self.df.dtypes.isin(dtypes)]







#-----------------------------------------------TO BE ADDED------------------------------------------------------
#     def visualize_df(self, variate_level, num_cols=False, cat_cols=False):
        
#         univariate analysis
#         if cat_cols:
#             cat_features = cols_with_dtype(dtype=["category"])
#              to be added - visualize plots..count plot
#             for col in cat_features:
#                 show_unique_values()
        
#         if num_cols:
#             num_features = cols_with_dtype(dtype=["int", "float"])
#              to be added - visualize plots...histograms

 
# outlier detection