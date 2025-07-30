extract_check_fetch_data

A lightweight Python package that provides utility functions for extracting request parameters, validating them, and fetching data from external APIs in Flask applications.

Features
extract_request_params(\*params_names)
Extracts multiple query parameters from incoming Flask requests and logs their values.

check_missing_params(params_dict)
Checks if required parameters are present and returns a JSON error response if any are missing.

fetch_data_from_external(url_key, params)
Sends a GET request to an external API with the provided parameters and handles errors gracefully.
