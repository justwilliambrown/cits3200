# Json

```py
import json
str_json = '{"name":"python","name1":"python1"}'
dic_json = json.loads(str_json)
print(dic_json)
#str->dic which matchs json's syntax

list_json ={ 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 } 
str_json_1 = json.dumps(list_json)
print(str_json_1)
#list or dic->str which matchs json's syntax

with open("test.json", "w") as write_file:
    json.dump(dic_json,write_file)
#   json.dump(str_json,write_file)
#   do not put a string as the first arg, the result will be like that "{\"name\":\"python\",\"name1\":\"python1\"}"
#   writing json dic to a file

with open("test.json", "r") as write_file:
    load_dict = json.load(write_file)
    print(load_dict)
# loading json file's information to process as dic
```
