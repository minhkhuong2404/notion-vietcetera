import json


with open('./vi_VN.jsonl', 'r') as json_file:
    json_list = list(json_file)

with open("facebook.txt", "w") as f:
    for json_str in json_list:
        result = json.loads(json_str)
        json.dump(result, f)
