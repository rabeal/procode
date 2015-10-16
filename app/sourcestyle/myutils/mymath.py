#!/usr/bin/python2.7 -tt

import pandas as pd

INDEX_OF_COUNT = 0
INDEX_OF_MEAN = 1
DESCRIBE_FEATURES_HEADER = ['count','mean','std','min','25per','50per','75per','max']

def get_list_describe_pandas_features(arr):
  df=pd.DataFrame(arr).describe()
  return [int(df.ix['count']),float(df.ix['mean']),float(df.ix['std']),float(df.ix['min']),float(df.ix['25%']),float(df.ix['50%']),float(df.ix['75%']),float(df.ix['max'])]


