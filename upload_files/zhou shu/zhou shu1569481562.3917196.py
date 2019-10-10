import json
str_json='{"name":"python","name1":"python1"}'
dir_json=json.loads(str_json)
print(type(dir_json))