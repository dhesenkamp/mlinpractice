#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base class for all of our feature extractors.

Created on Wed Sep 29 12:22:13 2021

@author: lbechberger
"""

from sklearn.base import BaseEstimator, TransformerMixin


class FeatureExtractor(BaseEstimator,TransformerMixin):
    """
    Base class for all feature extractors.
    inherits from BaseEstimator and 
    TransformerMixin (allowing for fit, transform, and fit_transform methods) from sklearn
    """
    

    def __init__(self, input_columns, feature_name):
        """
        Constructor
        calls super Constructor from BaseEstimator and TransformerMixin (initializes them)
        sets the respective _output_column and _feature_name
        """
        super(BaseEstimator, self).__init__()
        super(TransformerMixin, self).__init__()
        self._input_columns = input_columns
        self._feature_name = feature_name
        

    def get_feature_name(self):
        """Getter for feature name."""
        return self._feature_name
    

    def get_input_columns(self):
        """Getter for input columns."""
        return self._input_columns

    
    def _set_variables(self, inputs):
        """
        Set the internal variables based on input columns.
        Needs to be implemented by subclass!       
        """
        pass
    

    def fit(self, df):
        """Fit function: takes pandas DataFrame to set any internal variables"""
        inputs = []
        # collect all input columns from the DataFrame
        for input_col in self._input_columns:
            inputs.append(df[input_col])
        
        # call _set_variables
        self._set_variables(inputs)
        
        return self
    
         
    def _get_values(self, inputs):
        """
        Get preprocessed column based on the inputs from the DataFrame 
        and internal variables.
        Needs to be implemented by subclass.
        """
        pass
        

    def transform(self, df):
        """
        Transform function: transforms pandas DataFrame 
        based on any internal variables.
        """
        inputs = []
        # collect all input columns from the DataFrame
        for input_col in self._input_columns:
            inputs.append(df[input_col])
            
        return self._get_values(inputs)