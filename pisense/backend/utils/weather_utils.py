
import pandas as pd

from pisense.backend.models.weather_models import ALL_DAILY, ALL_HOURLY

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

# def map_to_models(df: pd.DataFrame, model_cls, field_map: dict[str, str]):
#     return [
#         model_cls(**{
#             model_field: float(getattr(row, df_field)) if "temperature" in model_field else getattr(row, df_field)
#             for model_field, df_field in field_map.items()
#         })
#         for row in df.itertuples(index=False)
#     ]

# map to models v3
def map_to_models(
    df,
    model_cls,
    field_map,
    float_fields=None,
    datetime_fields=None
):
    float_fields = float_fields or set()
    datetime_fields = datetime_fields or set()

    return [
        model_cls(**{
            model_field: (
                float(getattr(row, df_field)) if model_field in float_fields else
                pd.to_datetime(getattr(row, df_field)) if model_field in datetime_fields else
                getattr(row, df_field)
            )
            for model_field, df_field in field_map.items()
        })
        for row in df.itertuples(index=False)
    ]

def extract_fields(query_params):
    hourly_fields = []
    daily_fields = []

    for key, value in query_params.items():
        if value.lower() != "true":
            continue

        if key in ALL_HOURLY:
            hourly_fields.append(key)

        if key in ALL_DAILY:
            daily_fields.append(key)

    return hourly_fields, daily_fields
