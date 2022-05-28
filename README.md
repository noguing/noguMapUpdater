## ENVIRONMENT
python: 3.10  
packages: explore requirements.txt 

## WARNING
If you want to clone it and code by yourself, pay attention that there are many useless code in files. We will appreciate you if you can push a cleaner, faster or prettier code.

## CONFIGS
```json
{
  "osu_client": {
    "token": "your osu v2 client token",  // no use
    "id": 111111  // no use
  },
  "mongodb": {
    "host": "your mongodb server domain",
    "port": 27017,
    "user": "",
    "password": "",
    "database": "your mongodb database",
    "collection": "your mongodb collection in the database, default beatmapsets"
  },
  "osu_account": {
    "username": "your osu name",  // no use
    "password": "your osu password"  // no use
  },
  "get_map": {
    "beatmapset_save_type": "mongodb or file, default mongodb",  // mongodb please
    "proxy": {
      "server": "your proxy serverip:port, if null, no proxy. eg: http://127.0.0.1:54433"
    }
  }
}
```