# Harvester details

## Harvest process

Harvesters communicate with a [Galv server](https://github.com/galv-team/galv-backend) to upload data files.
The Harvester runs on a simple loop.
**Calls to the server are in bold.** *Server responses are in italics.*:
1. Check for settings updates, including new Monitored Paths
2. For each Monitored Path:
   1. For each file in the Monitored Path (recursively):
      1. Attempt to open the file using the appropriate parser
      2. If the file can be opened, **report the file size to the server**
      3. *The server responds with the file status.*
      4. If the status is one of 'STABLE' or 'RETRY IMPORT', the file is opened for parsing.
         1. **Report the file metadata scraped by the parser**
         2. **Report a summary of the file (first 10 rows for all columns)**
         3. *The server may respond with a mapping object, used to rename/rescale columns.*
         4. If no mapping object is returned, the file is left for later (user input required on the server side).
         5. The file contents are loaded into a Dask dataframe, and the mapping object is applied.
         6. **The dataframe is uploaded to the server as zipped .csv files.**
         7. Temporary files are deleted.

## Mapping object
The mapping object is a dictionary with the following structure:
```json
{
   "column_name_in_file": {
      "new_name": "new_column_name",
      "multiplier": 1.0,
      "addition": 0.0,
      "data_type": "bool|int|float|str|datetime64[ns]"
   }
}
```
Columns will be coerced to the specified data type.
Coercion is done using the `pd.Series.asdtype()` function, except for datetime64[ns] columns,
which are coerced using `pd.to_datetime(x)`.

Numerical (int/float) columns will be rebased and rescaled according to the `multiplier` and `addition` fields.
New column values = (old column values + `addition`) * `multiplier`.
