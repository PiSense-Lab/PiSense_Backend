from pisense.backend.tests import plus
from pisense.backend.read_inputs import Reader
from pisense.backend.read_inputs import xclReader
from pisense.backend.read_inputs import csvReader
import pandas as pd
import json



def test_plus(): # Temporary testing for pytest, should be removed once we have real code
    ret = plus(1, 1)
    assert ret == 2

class TestReaders():

    f = pd.read_excel("./tests/ExampleData.xlsx", "Sheet1")
    f.to_csv("./tests/ExampleData.csv")

    xFilepath = "./tests/ExampleData.xlsx"
    cFilepath = "./tests/ExampleData.csv"
    
    # def test_fails(self):
    #    assert False

    def test_Pass(self):
        assert True

    def test_xReadIn(self):
        xRead = xclReader(self.xFilepath)
        xList = xRead.readIn(self.xFilepath)
        assert isinstance(xList[0], pd.DataFrame)

    def test_cReadIn(self):
        cRead = csvReader(self.cFilepath)
        cList = cRead.readIn(self.cFilepath)
        #assert cList == 1
        assert isinstance(cList[0], pd.DataFrame)

    def test_toJSON(self):
        cRead = csvReader(self.cFilepath)
        cList = cRead.readIn(self.cFilepath)
        cjson = cRead.toJSON(1)
        tf = False
        try:
            json.loads(cjson)
            tf = True
        except ValueError as e:
            tf = False
        assert tf



