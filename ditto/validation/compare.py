# coding: utf8

import numpy as np
import pandas as pd
import argparse



def rms(df1, df2, key):
    '''Computes root mean squares on the given key.

'''
    rms=[]
    for i1,row1 in df1.iterrows():
        for i2,row2 in df2.iterrows():
            if row1['Bus']==row2['Bus']:
                try:
                    rms.append((row1[key]-row2[key])**2)
                except:
                    raise ValueError('{} not in dataframe'.format(key))
    return sum(rms)


def absolute(df1, df2, key):
    '''Computes sum of the absolute differences on the given key.

'''
    abss=[]
    for i1,row1 in df1.iterrows():
        for i2,row2 in df2.iterrows():
            if row1['Bus']==row2['Bus']:
                try:
                    abss.append(abs(row1[key]-row2[key]))
                except:
                    raise ValueError('{} not in dataframe'.format(key))
    return sum(abss)


def main():
    '''Compare two power flow results.

**Usage:**

$ python compare.py -p1 ./inputs/opendss/ieee_13_node -p2 ./outputs/from_cyme/to_opendss/ieee_13_node

This will look for "voltage_profile.csv" in both directories and load them into a Pandas dataframe.

For now, this only computes the root mean square error for each phase (in p.u).

'''
    #Parse the arguments
    parser=argparse.ArgumentParser()

    #Feeder list
    parser.add_argument('-p1', action='store', dest='path1')

    #Format from
    parser.add_argument('-p2', action='store', dest='path2')

    results=parser.parse_args()

    path1=results.path1
    path2=results.path2

    df1=pd.read_csv(path1+'/voltage_profile.csv')
    df2=pd.read_csv(path2+'/voltage_profile.csv')

    #RMS
    for p,k in zip(['A','B','C'],[' pu1', ' pu2', ' pu3']):
        print('Phase {p} : rms={r}'.format(p=p,r=rms(df1,df2,k)))

    #Absolute
    for p,k in zip(['A','B','C'],[' pu1', ' pu2', ' pu3']):
        print('Phase {p} : |error|={r}'.format(p=p,r=absolute(df1,df2,k)))

if __name__ == '__main__':
    main()
