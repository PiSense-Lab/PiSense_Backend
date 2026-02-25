import pandas as pd
import mariadb
from sqlalchemy import create_engine


try:
    creation_string = "mariadb://admin:ilovepisense@192.158.1.90:3306/PiSensee"
    engine = create_engine(creation_string)
except Exception as e:
    print(f"Error connecting to d: {e}")


def toJSON(df):
    return df.to_json()


# Writes a DataFrame to the MariaDB database given
#   by the engine named at the top of the file.
#   if_exists mode can either be 'replace' or 'append'.
def toSQL(df, tablename, mode="replace"):
    try:
        df.to_sql(
            tablename,
            con=engine,
            if_exists=mode,
            index=False)
        return 200  # Change once actually connected
    except Exception as e:
        print(f"Error sending DataFrame to database: {e}")
        return 404


# reads the table given by tablename and returns a pd.DataFrame
#   con is the SQLAlchemy engine named at the top of the file.
def readSQL(tableName):
    try:
        return pd.read_sql_table(tableName, con=engine)
    except Exception as e:
        print(f"Error reading database: {e}")
        return 404


# list_of_values must be formatted
#   [{col_name(time) : value(time), col_name(measurement) : value(measurement)]
def addRow(df, list_of_values, loca=-1):
    try:
        # eventually have sorted by timestamp
        # left = 0
        # right = len(df.column[0])
        # while left <= right:
        #    mid = (left + right) // 2
        #    if arr[mid] == target:
        #        return mid
        #    elif arr[mid] < target:
        #        left = mid + 1
        #    else:
        #        right = mid - 1
        if loca != -1:
            df.loc[loca] = list_of_values
        else:
            df.loc[len(df)] = list_of_values
        return df
    except Exception as e:
        return print(e)


def editRow(df, row, col, value):
    try:
        df.loc[row, col] = value
        return 1
    except Exception as e:
        print(f"Error editing row: {e}")
        return -1
