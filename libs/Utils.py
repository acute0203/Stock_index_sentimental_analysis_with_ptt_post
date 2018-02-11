import json
class Utils():
    
    def write_json_to_file(json_data, json_file_path):
        with open(json_file_path, 'w') as out_file:
            json.dump(json_data, out_file)
        return 1

    def read_json_from_file(json_file_path):
        with open(json_file_path) as data_file:  
            data = json.load(data_file)
        return data