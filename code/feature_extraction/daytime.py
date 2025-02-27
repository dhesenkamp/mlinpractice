# -*- coding: utf-8 -*-
"""
Extracts time from a tweet and one-hot encodes it.

Created on Sat Oct 23 17:51:46 2021

@author: Yannik
modified by dhesenkamp
"""

from code.feature_extraction.feature_extractor import FeatureExtractor
import numpy as np
import pandas as pd


class Daytime(FeatureExtractor):
    """Extracting time from a given input_column"""
    
    def __init__(self, input_column):
        """Constructor with given input_column."""
        super().__init__([input_column], "day_{0}".format(input_column))
        
        
    # don't need to fit, so don't overwrite _set_variables()
        
        
    def _get_values(self, inputs):
        """
        Extracts the hour tweet was posted and sets it as a daytime.
        After that it one-hot encodes the array before return.
        """
        daytime = []
        for i in inputs[0]:
            time = i.split(":")
            hour = int(time[0])
            
            # night hours
            if hour in range(0, 5):
                daytime.append(0)
            
            # morning hours
            if hour in range(5, 10):
                daytime.append(1)
                
            # midday
            if hour in range(10, 15):
                daytime.append(2)
                
            # afternoon
            if hour in range(15, 19):
                daytime.append(3)
                
            # evening hours
            if hour in range(19, 24):
                daytime.append(4)
        
        # one-hot encoding
        result = np.array(pd.get_dummies(daytime))
        
        return result