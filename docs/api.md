## API Documentation

[/weather](#/weather)
[/datatables](#/datatables)
[/user](#/user)


### /weather

#### ~/forecast-weather
##### ~/hourly

##### ~/daily


#### ~/historical-weather
##### ~/hourly

##### ~/daily


### /datatables


#### ~/
Gets and returns all tables within a project.

params:
  `project_id`: int

returns: TODO

responses:
  codes:
    200 - Successful Response, getting tables succeeded and returned value.
    422 - Validation Error, tables returned did not fit the return validation type. Returns JSON with ...
      `{"detail": [
        {
          "loc": [
            "string",
            0
          ],
          "msg": "string",
          "type": "string",
          "input": "string",
          "ctx": {}type"
        }
      ]}`

#### ~/{tablename}
Gets the inputted table and returns the entire table 
:::backend.routes.datasheets.read_single_table

#### ~/edit_point
:::backend.routes.datasheets.edit_point

#### ~/add_point
:::backend.routes.datasheets.add_point

#### ~/remove_point
:::backend.routes.datasheets.remove_point

#### ~/upload_manual
:::backend.routes.datasheets.upload_manual

#### ~/upload_csv
:::backend.routes.datasheets.upload_csv

#### ~/upload_excel_file
:::backend.routes.datasheets.upload_excel_file

### /user


