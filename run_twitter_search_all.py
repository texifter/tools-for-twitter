import argparse
import copy
import json
import logging
import math
import os
import requests
import time
from requests.auth import HTTPBasicAuth
from utils import RateLimitedFetcher

logFormatter = logging.Formatter("[%(asctime)s] %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

fetcher = RateLimitedFetcher(logger, 1000)

def write_json_output(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile)

def get_bearer_token(api_key, api_secret_key):
    token_url = 'https://api.twitter.com/oauth2/token'
    payload = {'grant_type': 'client_credentials'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    response = requests.request('POST', token_url, 
        auth=HTTPBasicAuth(api_key, api_secret_key), 
        data=payload, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"could not get bearer token: {e}")
    as_json = json.loads(response.text)
    return as_json['access_token']

def get_result_set(bearer_token, query_params, next_token=None, page=1):
    query_url = 'https://api.twitter.com/2/tweets/search/all'
    params_to_use = copy.deepcopy(query_params)
    if next_token:
        params_to_use['next_token'] = next_token
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = fetcher.get_or_wait(query_url, query_params=params_to_use, headers=headers)
    if response.code != 200:
        raise Exception(f"error getting result set: {response.code}: {response.data}")
    return response.data

def load_configuration(config_file):
    with open(config_file) as config_input:
        config = json.load(config_input)

        if not 'api_key' in config:
            raise Exception("configuration is missing api_key")
        if not 'api_secret' in config:
            raise Exception("configuration is missing api_secret")
        if not 'output_path' in config:
            raise Exception("configuration is missing output_path")
        if not 'search_parameters' in config:
            raise Exception("configuration is missing search_parameters")

        return config
       
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration file")
    args = parser.parse_args()

    if not args.config:
        raise Exception("Missing configuration parameter")

    configuration = load_configuration(args.config)
    if 'log_to_file' in configuration and configuration['log_to_file']:
        if not 'log_file_path' in configuration:
            raise Exception('log_to_file set to true, but log_file_path is not set in configuration')        

        if not os.path.exists(configuration['log_file_path']):
            os.makedirs(configuration['log_file_path'])
        log_filename = f'{math.floor(time.time())}_twitter_search_all.log'

        fileHandler = logging.FileHandler(os.path.join(configuration['log_file_path'], f"{log_filename}.log"))
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)

    output_path = configuration['output_path']
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    logger.info("Getting bearer token...")
    bearer_token = get_bearer_token(configuration['api_key'], configuration['api_secret'])

    if not bearer_token:
        raise Exception('no authorization bearer token found')

    page_num = 1
    next_token = None
    search_params = configuration['search_parameters']
    while True:
        logger.info(f"Getting page number {page_num}")

        response = get_result_set(bearer_token, search_params, next_token=next_token, page=page_num)
        logger.info(f"Got page number {page_num} response, writing...")

        filepath = os.path.join(output_path, f'data_file_{page_num}.json')
        write_json_output(filepath, response)
        logger.info(f"Data file written for page {page_num}")

        if 'meta' in response and 'next_token' in response['meta']:
            next_token = response['meta']['next_token']
            page_num = page_num + 1
        else:
            break
