from atrax import DataSet
from atrax import Atrax as tx
from .utils import rolling_mean

def prep_data(ds: DataSet, sale_col) -> DataSet:
    """
    Preprocess the dataset by setting up the date column.
    
    Args:
        ds (DataSet): The dataset to preprocess.
        
    Returns:
        DataSet: The preprocessed dataset with NaN values removed.
    """
    dt_list = ds[sale_col]
    print(type(dt_list))
    ds[sale_col] = tx.to_datetime(dt_list)
    ds = ds.sort(sale_col)

    ds['trend'] = rolling_mean(ds[sale_col], window=7)
    ds['day_of_week'] = ds[sale_col].dt.dayofweek
    ds['is_weekend'] = ds[sale_col].isin([5,6]).astype(int)
    ds['lag_1'] = ds[sale_col].shift(1)
    ds['lag_2'] = ds[sale_col].shift(7)
    ds['lag_mean_1_7'] = ds[['lag_1', 'lag_2']].mean(axis=1)

    return ds

    