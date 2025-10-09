# matrix_api

Matrix API definition is available here: https://app.swaggerhub.com/apis/matrixreq/MatrixALM_QMS/2.5

Create a 'config.json' file at root level of the python script. It shall contain:

```json
{
    "url": "https://mycompany.matrixreq.com/rest/1",
    "token": "api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "project": "matrix_project_name"
}
```

### Example of usage:

```
matrix_api git:(main) ✗ python matrix_api.py --help
usage: matrix_api.py [-h] -f FOLDER_ID -i ITEM_ID

options:
  -h, --help            show this help message and exit
  -f FOLDER_ID, --folder_id FOLDER_ID
                        Folder ID from which items will be exported
  -i ITEM_ID, --item_id ITEM_ID
                        Folder ID from which items will be exported
```

```
python matrix_api.py -f F-SRS-2 -i SRS-1
```

```
matrix_api git:(main) ✗ python matrix_export.py --help
usage: matrix_export.py [-h] [-o OUTPUT_FILENAME] -f FOLDER_ID

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILENAME, --output_filename OUTPUT_FILENAME
                        HTML format, default is 'output.html'
  -f FOLDER_ID, --folder_id FOLDER_ID
                        Folder ID from which items will be exported
```

```
python matrix_export.py -o export -f F-PREQ-16 
python matrix_export.py -o export -f F-FMEA-2
```

It does export the data table files called `export.html` / `export.xlsx`
