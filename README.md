## ENVIRONMENT
python: 3.10  
packages: explore requirements.txt 

## CONFIGS
```json
{
  "osu_client": {
    "token": "your osu v2 client token",
    "id": 111111
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
    "username": "your osu name",
    "password": "your osu password"
  },
  "get_map": {
    "beatmapset_save_type": "mongodb or file, default mongodb",
    "proxy": {
      "server": "your proxy serverip:port, if null, no proxy. eg: http://127.0.0.1:54433"
    }
  }
}
```