# pisense/backend/read_inputs.py
import pandas as pd
import numpy as np


# base class of Reader to be inherited by various input file readers
class Reader():
    filepath = "path_to_file"
    sheetList = []

    def __init__(self, fPath, list=[]):
        self.filepath = fPath
        self.sheetList = list

    def toJSON(self, sheetNum=1):
        return self.sheetList[sheetNum - 1].to_json()


# reader and other functions for altering excel (xlsx) files
class xclReader(Reader):
    # reads in a xlsx file and returns an array with the sheets in each
    #   index of the array. The array is comprised of pandas DataFrames
    def readIn(self):
        with pd.ExcelFile(self.filepath) as xls:
            for index, pd.sheet_names in enumerate(pd.sheet_names):
                self.sheetList.append(pd.read_excel(
                   xls, pd.sheet_names[index]))
        return self.sheetList

    # gets the columns inbetween the firstCol and endCol and returns the
    #   DataFrame
    def getCols(self, firstCol, endCol, sheetName):
        return pd.read_excel(self.filepath, sheetName)
        # usecols=firstCol:endCol)

    # gets the rows in between the firstRow and endRow
    def getRows(self, firstRow, endRow, sheetName):
        return pd.read_excel(self.filepath, sheetName)


# reader and other functions for altering csv files
class csvReader(Reader):
    def readIn(self, filepath):
        self.sheetList.append(pd.read_csv(filepath))
        return self.sheetList
