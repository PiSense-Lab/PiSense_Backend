from pisense.backend.read_inputs import Reader
from pisense.backend.read_inputs import xclReader
from pisense.backend.read_inputs import csvReader
import pandas as pd
import json
from pisense.backend.utils.dataframe_utils import toJSON, addRow, editRow, toSQL, readSQL
from sqlalchemy import create_engine
import mariadb


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
        cjson = toJSON(cList[0])
        tf = False
        try:
            json.loads(cjson)
            tf = True
        except ValueError as e:
            tf = False
        assert tf

    def test_addRow(self):
        cRead = csvReader(self.cFilepath)
        cList = cRead.readIn(self.cFilepath)
        # print(cList[0])
        # print(cList[0].columns)
        new_df = addRow(cList[0], list_of_values={
            cList[0].columns[0] : '10:03:00', cList[0].columns[1] : 15
        })
        # print(new_df)
        assert new_df.at[len(new_df) - 1,"Value"] == 15
        second_df = addRow(cList[0], list_of_values={
            cList[0].columns[0] : '10:01:00', cList[0].columns[1] : 32
        }, loca=5)
        print(second_df)
        assert second_df.at[5, "Value"] == 32

    def test_editRow(self):
        assert True

    # def test_toSQL_readSQL(self):
    #    try:
    #        conn = mariadb.connect(
    #        user="admin",
    #        password="ilovepisensee",
    #        host="192.168.1.90",
    #        port=3306,
    #        database="PiSense"
    #        )

    #        cRead = csvReader(self.cFilepath)
    #        cList = cRead.readIn(self.cFilepath)
    #        toSQL(cList[0], "test_table", conn)
    #        temp = readSQL("test_table", conn)

    #        assert cList[0].at(5, "Value") == temp.at(5, "Value") # must test after connected to db
    #    except Exception as e:
    #        print(f"Error connecting to MariaDB Platform: {e}")
            # creation_string = "mariadb://admin:ilovepisense@192.158.1.90:3306/PiSensee"
            # engine = create_engine(creation_string)
