
import pandas as pd

# helper function to build datetime index from the block's time, time_end, and interval
def build_datetime_index(block) -> pd.DatetimeIndex:
    return pd.date_range(
        start=pd.to_datetime(block.Time(), unit="s", utc=True),
        end=pd.to_datetime(block.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=block.Interval()),
        inclusive="left"
    )

# helper function to build records from the block and variable map
def build_dataframe(block, variable_map: dict[str, int]) -> pd.DataFrame:
    data = {
        name: block.Variables(idx).ValuesAsNumpy()
        for name, idx in variable_map.items()
    }

    df = pd.DataFrame(data)
    df["datetime"] = build_datetime_index(block)

    return df

# helper function to split datetime into date and time columns
def add_date_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.time
    return df

# set of fields to convert to float, set of fields to convert to datetime, and the rest are left as is
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


