import requests
import json
import time


def poller(url, poll_interval):
    """
    Function for polling the REopt API results URL until status is not "Optimizing..."
    :param url: results url to poll
    :param poll_interval: seconds
    :return: dictionary response (once status is not "Optimizing...")
    """
    key_error_count = 0
    key_error_threshold = 4
    status = "Optimizing..."
    print("Polling {} for results with interval of {}s...".format(url, poll_interval))
    while True:

        resp = requests.get(url=url, verify=False)
        resp_dict = json.loads(resp.text)

        try:
            status = resp_dict['outputs']['Scenario']['status']
        except KeyError:
            key_error_count += 1
            print('KeyError count: {}'.format(key_error_count))
            if key_error_count > key_error_threshold:
                print('Breaking polling loop due to KeyError count threshold of {} exceeded.'.format(key_error_threshold))
                break

        if status != "Optimizing...":
            time.sleep(poll_interval)
            resp = requests.get(url=url, verify=False)
            resp_dict = json.loads(resp.text)
            break
        else:
            # Add extra sleep time for slower-responding localhost calls
            # even while results are expected to be in response after status != "Optimizing..."
            time.sleep(poll_interval)

    return resp_dict

def reo_optimize(post, API_KEY, root_url='https://developer.nrel.gov/api/reopt', poll_interval=10):
    """
    Function for polling the REopt API results URL until status is not "Optimizing..."
    :post: the API reo /job endpoint POST which define the Scenario with user inputs
    :param API_KEY: API key for accessing API on NREL's production server
    :param root_url: location of the API to poll; use 'http://localhost:8000' for localhost, not 0.0.0.0.8000
    :param poll_interval: seconds
    :return: dictionary response (once status is not "Optimizing...")
    """
    
    post_url = root_url + '/v1/job/?api_key=' + API_KEY
    results_url = root_url + '/v1/job/<run_uuid>/results/?api_key=' + API_KEY
    
    resp = requests.post(url=post_url, json=post)

    if not resp.ok:
        print("Status code {}. {}".format(resp.status_code, resp.content))
    else:
        print("Response OK from {}.".format(post_url))
        run_id_dict = json.loads(resp.text)

        try:
            run_id = run_id_dict['run_uuid']
        except KeyError:
            msg = "Response from {} did not contain run_uuid.".format(post_url)

        return poller(url=results_url.replace('<run_uuid>', run_id), poll_interval=poll_interval)
