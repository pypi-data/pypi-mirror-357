# profiler.py

import pandas as pd
import numpy as np

def profile_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs a detailed exploratory data analysis on a pandas DataFrame.

    This function generates a comprehensive statistical summary for each column,
    differentiating between numerical and categorical data types to provide
    relevant metrics for each.

    Args:
        df (pd.DataFrame): The input DataFrame to analyze.

    Returns:
        pd.DataFrame: A DataFrame where each row corresponds to a column from the
                      input df and each column is a calculated statistic.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    print(f"Profiling pandas DataFrame: {df.shape[0]} rows, {df.shape[1]} columns")
    print("-" * 30)

    stats_list = []
    for col in df.columns:
        # Basic Info
        non_missing_count = df[col].count()
        missing_count = df[col].isnull().sum()
        missing_percent = (missing_count / len(df)) * 100 if len(df) > 0 else 0
        
        col_stats = {
            'column_name': col,
            'dtype': df[col].dtype,
            'non_missing_count': non_missing_count,
            'missing_count': missing_count,
            'missing_percent': f"{missing_percent:.2f}%"
        }
        
        # --- FIX: Added 'and not pd.api.types.is_bool_dtype(df[col])' ---
        # This now correctly separates numeric columns from boolean columns.
        if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
            # Numerical statistics
            p = df[col].quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99])
            iqr = p.get(0.75, np.nan) - p.get(0.25, np.nan)
            mean_val = df[col].mean()
            std_dev = df[col].std()
            cv = (std_dev / mean_val) * 100 if mean_val != 0 else np.nan

            numerical_stats = {
                'mean': mean_val, 'std_dev': std_dev, 'coeff_of_variation': cv,
                'skewness': df[col].skew(), 'kurtosis': df[col].kurt(),
                'num_zeros': (df[col] == 0).sum(), 'min': df[col].min(),
                'percentile_1': p.get(0.01), 'percentile_5': p.get(0.05),
                'percentile_10': p.get(0.10), 'percentile_25': p.get(0.25),
                'percentile_50_median': p.get(0.50), 'percentile_75': p.get(0.75),
                'iqr': iqr, 'percentile_90': p.get(0.90), 'percentile_95': p.get(0.95),
                'percentile_99': p.get(0.99), 'max': df[col].max(),
            }
            col_stats.update(numerical_stats)
        else: # Handles boolean, categorical, object, etc.
            unique_vals = df[col].dropna().unique()
            col_stats['unique_count'] = len(unique_vals)
            col_stats['unique_values_list'] = f"High Cardinality ({len(unique_vals)})" if len(unique_vals) > 10 else list(unique_vals)
            
            if non_missing_count > 0:
                mode_series = df[col].mode()
                if not mode_series.empty:
                    mode_val = mode_series.iloc[0]
                    col_stats['mode'] = mode_val
                    col_stats['mode_frequency'] = df[col].value_counts().get(mode_val, 0)
                    col_stats['mode_percent'] = f"{(col_stats['mode_frequency'] / non_missing_count) * 100:.2f}%"

        stats_list.append(col_stats)

    summary_df = pd.DataFrame(stats_list).set_index('column_name')
    column_order = [
        'dtype', 'non_missing_count', 'missing_count', 'missing_percent', 'unique_count', 
        'unique_values_list', 'mode', 'mode_frequency', 'mode_percent', 'mean', 'std_dev', 
        'coeff_of_variation', 'skewness', 'kurtosis', 'num_zeros', 'min', 'percentile_1', 
        'percentile_5', 'percentile_10', 'percentile_25', 'percentile_50_median', 
        'percentile_75', 'iqr', 'percentile_90', 'percentile_95', 'percentile_99', 'max'
    ]
    return summary_df.reindex(columns=column_order)
