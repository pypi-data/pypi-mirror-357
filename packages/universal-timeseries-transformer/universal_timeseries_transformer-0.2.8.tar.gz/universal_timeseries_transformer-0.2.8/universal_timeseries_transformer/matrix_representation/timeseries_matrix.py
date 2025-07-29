import numpy as np
from functools import partial, cached_property
from typing import Optional, List, Any, Union
import pandas as pd
from universal_timeseries_transformer.timeseries_transformer import transform_timeseries
from universal_timeseries_transformer.timeseries_application import (
    transform_timeseries_to_cumreturns_ref_by_series,
    transform_timeseries_to_cumreturns,
    transform_timeseries_to_returns,
)
from universal_timeseries_transformer.timeseries_slicer import slice_timeseries_around_index

class TimeseriesMatrix:
    """
    Time series matrix wrapper with lazy-loaded transformations.
    
    Cached Properties:
        basis: Index values as numpy array
        dates: Index values as list
        date_i: First date in series
        date_f: Last date in series
        returns: Calculated returns DataFrame
        cumreturns: Calculated cumulative returns DataFrame
        datetime: DataFrame with datetime index
        unixtime: DataFrame with unix timestamp index
        string: DataFrame with string index
    
    Manual Cache Properties:
        cumreturns_ref: Reference-based cumulative returns DataFrame (needs invalidation)
    """
    
    def __init__(self, df: pd.DataFrame, index_ref: Optional[str] = None) -> None:
        self.df = df
        self.index_ref = index_ref
        self.srs_ref = self.set_srs_ref()
        
        # Only cumreturns_ref needs manual cache (due to dynamic method attachment)
        self._cumreturns_ref: Optional[pd.DataFrame] = None

    @cached_property
    def basis(self) -> np.ndarray:
        return self.df.index.values

    @cached_property
    def dates(self) -> List[Any]:
        return list(self.basis)

    @cached_property
    def date_i(self) -> Any:
        return self.dates[0]
    
    @cached_property
    def date_f(self) -> Any:
        return self.dates[-1]

    @cached_property
    def datetime(self) -> pd.DataFrame:
        return transform_timeseries(self.df, 'datetime')

    @cached_property
    def unixtime(self) -> pd.DataFrame:
        return transform_timeseries(self.df, 'unix_timestamp')

    @cached_property
    def string(self) -> pd.DataFrame:
        return transform_timeseries(self.df, 'str')

    @cached_property
    def returns(self) -> pd.DataFrame:
        return transform_timeseries_to_returns(self.df)

    @cached_property
    def cumreturns(self) -> pd.DataFrame:
        return transform_timeseries_to_cumreturns(self.df)
    
    def row(self, i: int) -> pd.DataFrame:
        return self.df.iloc[[i], :]

    def column(self, j: int) -> pd.DataFrame:
        return self.df.iloc[:, [j]]
        
    def row_by_name(self, name: str) -> pd.DataFrame:
        return self.df.loc[[name], :]

    def column_by_name(self, name: str) -> pd.DataFrame:
        return self.df.loc[:, [name]]

    def component(self, i: int, j: int) -> Any:
        return self.df.iloc[i, j]

    def component_by_name(self, name_i: str, name_j: str) -> Any:
        return self.df.loc[name_i, name_j]

    def rows(self, i_list: List[int]) -> pd.DataFrame:
        return self.df.iloc[i_list, :]
        
    def columns(self, j_list: List[int]) -> pd.DataFrame:
        return self.df.iloc[:, j_list]

    def rows_by_names(self, names: List[str]) -> pd.DataFrame:
        return self.df.loc[names, :]
        
    def columns_by_names(self, names: List[str]) -> pd.DataFrame:
        return self.df.loc[:, names]

    @property
    def cumreturns_ref(self) -> pd.DataFrame:
        if self.index_ref is None:
            raise ValueError("Cannot calculate cumreturns_ref: no reference index set")
        if self._cumreturns_ref is None:
            df = transform_timeseries_to_cumreturns_ref_by_series(self.df, self.srs_ref)
            df.slice = partial(self.slice_cumreturns_ref)
            df.slice_by_name = partial(self.slice_cumreturns_ref_by_name)
            self._cumreturns_ref = df
        return self._cumreturns_ref

    def set_srs_ref(self) -> Optional[pd.Series]:
        if self.index_ref is not None:
            return self.row_by_name(self.index_ref).iloc[0]
        else:
            return None

    def slice_cumreturns_ref(self, index_start: int, index_end: int) -> Optional[pd.DataFrame]:
        if self._cumreturns_ref is None:
            return None
        return slice_timeseries_around_index(
            timeseries=self._cumreturns_ref, 
            index_ref=self.index_ref, 
            index_start=index_start, 
            index_end=index_end
        )

    def slice_cumreturns_ref_by_name(self, name_start: str, name_end: str) -> Optional[pd.DataFrame]:
        if self._cumreturns_ref is None:
            return None
        return self._cumreturns_ref.loc[name_start:name_end]