import hashlib
import json
import os.path
import random
import string
import yaml

from ate.exception import ParamsError


def gen_random_string(str_len):
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len))

def gen_md5(str_list):
    authorization_str = "".join(str_list)
    return hashlib.md5(authorization_str.encode('utf-8')).hexdigest()

def handle_req_data(data):
    if not data:
        return data

    if isinstance(data, str):
        # check if data in str can be converted to dict
        try:
            data = json.loads(data)
        except ValueError:
            pass

    if isinstance(data, dict):
        # sort data in dict with keys, then convert to str
        data = json.dumps(data, sort_keys=True)

    return data

def load_yaml_file(yaml_file):
    with open(yaml_file, 'r+') as stream:
        return yaml.load(stream)

def load_json_file(json_file):
    with open(json_file) as data_file:
        return json.load(data_file)

def load_testcases(testcase_file_path):
    file_suffix = os.path.splitext(testcase_file_path)[1]
    if file_suffix == '.json':
        return load_json_file(testcase_file_path)
    elif file_suffix in ['.yaml', '.yml']:
        return load_yaml_file(testcase_file_path)
    else:
        # '' or other suffix
        raise ParamsError("Bad testcase file name!")

def parse_response_object(resp_obj):
    try:
        resp_body = resp_obj.json()
    except ValueError:
        resp_body = resp_obj.text

    return {
        'status_code': resp_obj.status_code,
        'headers': resp_obj.headers,
        'body': resp_body
    }

def diff_json(current_json, expected_json):
    json_diff = {}

    for key, expected_value in expected_json.items():
        value = current_json.get(key, None)
        if str(value) != str(expected_value):
            json_diff[key] = {
                'value': value,
                'expected': expected_value
            }

    return json_diff

def diff_response(resp_obj, expected_resp_json):
    diff_content = {}
    resp_info = parse_response_object(resp_obj)

    expected_status_code = expected_resp_json.get('status_code', 200)
    if resp_info['status_code'] != int(expected_status_code):
        diff_content['status_code'] = {
            'value': resp_info['status_code'],
            'expected': expected_status_code
        }

    expected_headers = expected_resp_json.get('headers', {})
    headers_diff = diff_json(resp_info['headers'], expected_headers)
    if headers_diff:
        diff_content['headers'] = headers_diff

    expected_body = expected_resp_json.get('body', None)

    if expected_body is None:
        body_diff = {}
    elif type(expected_body) != type(resp_info['body']):
        body_diff = {
            'value': resp_info['body'],
            'expected': expected_body
        }
    elif isinstance(expected_body, str):
        if expected_body != resp_info['body']:
            body_diff = {
                'value': resp_info['body'],
                'expected': expected_body
            }
    elif isinstance(expected_body, dict):
        body_diff = diff_json(resp_info['body'], expected_body)

    if body_diff:
        diff_content['body'] = body_diff

    return diff_content
