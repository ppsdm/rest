# cat-rest-python
rest api server untuk ppsdm cat

`/get` expected output

```
{
  "cfit" : [1,3],
  "apm" : [2,5],
  "papikostik" : {
    "a" : 3,
    "b" : 4,
    "c" : 2,
    ...
  },
  "pcas" : {
    "e" : 3,
    "n" : 2,
    ...
  }
}
```

## Installing

1. Clone repository

2. Change to project directory
    ```
    $ cd cat-rest-python
    ```

3. Install required dependencies
    ```
    $ pip install -r requirements.txt
    ```

## Usage
Run application by executing:

```
python restapi.py
```
or using flask command:

```
FLASK_APP=restapi.py flask run
```

## TAO ITEM NAMING CONVENTION
1. APM 
  ```
  itemResult identifier="APM_1"
  ```