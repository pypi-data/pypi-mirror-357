from flask import jsonify, request
import logging
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_request_params(*params_names):
    params = []
    for param_name in params_names:
        param_value = request.args.get(param_name)
        params.append(param_value)
        logger.debug(f"Incoming param: {param_name}={param_value}")
    return tuple(params)


def check_missing_params(params_dict):
    missing_params = []
    for param, value in params_dict.items():
        if not value:
            logger.warning(f"{param} parameter is missing")
            missing_params.append(param)

    if missing_params:
        error_message = f"The following parameters are required: {', '.join(missing_params)}"
        return jsonify({"error": error_message}), 400
    return None


def fetch_data_from_external(url_key, params):
    try:
        response = requests.get(url_key, params=params)
        response.raise_for_status()
        logger.info(f"Successfully fetched data from {url_key} with params: {params}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from {url_key} with params: {params}. Error: {e}")
        raise