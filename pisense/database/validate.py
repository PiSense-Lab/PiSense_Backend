class ValidationError(Exception):
    pass
def validate_value(value, col_type):
    col_type = col_type.upper()
    
    if col_type == "INT":
        try:
            int(value)
        except ValueError:
            raise ValidationError("Value is not INT")
    elif col_type == "DECIMAL":
        try:
            float(value)
        except ValueError:
            raise ValidationError("Value is not DECIMAL")    
    elif col_type.startswith("VARCHAR"):
        max_len = int(col_type[col_type.find("(")+1 : col_type.find(")")])
        if len(str(value)) > max_len:
            raise ValidationError("Value is not correct length")
    elif col_type == "DATE":
        import datetime
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Value is not valid date")
    elif col_type == "TIME":
        import datetime
        try:
            datetime.datetime.strptime(value, "%H:%M:%S")
        except ValueError:
            raise ValidationError("Value is not valid time")
    elif col_type == "BOOL":
        try:
            # Accept Python booleans
            if isinstance(value, bool):
                pass
            else:
                raise ValueError()
        except ValueError:
            raise ValidationError("Value is not valid bool")
        
