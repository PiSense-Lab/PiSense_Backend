
import pandas as pd

def build_datetime_index(block) -> pd.DatetimeIndex:
    return pd.date_range(
        start=pd.to_datetime(block.Time(), unit="s", utc=True),
        end=pd.to_datetime(block.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=block.Interval()),
        inclusive="left"
    )

def build_dataframe(block, variable_map: dict[str, int]) -> pd.DataFrame:
    data = {
        name: block.Variables(idx).ValuesAsNumpy()
        for name, idx in variable_map.items()
    }

    df = pd.DataFrame(data)
    df["datetime"] = build_datetime_index(block)

    return df

def add_date_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.time
    return df

# def map_to_models(df, model_cls, field_map, float_fields: set[str]):
#     return [
#         model_cls(**{
#             model_field: float(getattr(row, df_field)) if model_field in float_fields else getattr(row, df_field)
#             for model_field, df_field in field_map.items()
#         })
#         for row in df.itertuples(index=False)
#     ]

def map_to_models(df: pd.DataFrame, model_cls, field_map: dict[str, str]):
    return [
        model_cls(**{
            model_field: float(getattr(row, df_field)) if "temperature" in model_field else getattr(row, df_field)
            for model_field, df_field in field_map.items()
        })
        for row in df.itertuples(index=False)
    ]
