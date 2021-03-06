import json
import requests
import time

SECONDS_PER_HOUR = (60 * 60)


class ResponseItem():
    def __init__(self, response_code, response_data):
        self.code = response_code
        self.data = response_data
        self.is_rate_limited = False
        self.wait_until = 0.0


class RateLimitedFetcher():
    def __init__(self, logger, requests_per_hour):
        self._requests_per_hour = requests_per_hour
        self._current_requests = 0
        self._next_reset_time = 0
        self._logger = logger

    def _check_reset_timer(self):
        if time.time() < self._next_reset_time:
            return False
        self._next_reset_time = time.time() + SECONDS_PER_HOUR + 10
        self._current_requests = 0
        return True

    def _check_current_limit(self):
        if self._next_reset_time == 0:
            self._next_reset_time = time.time() + SECONDS_PER_HOUR + 10

        if self._current_requests >= self._requests_per_hour:
            if not self._check_reset_timer():
                return False

        return True

    def _wait_time_delta(self, until_timestamp):
        current_time = time.time()
        delta = until_timestamp - current_time
        if delta < 0.0:
            return "(passed)"
        minutes = math.floor(delta / 60)
        seconds = math.floor(delta % 60)
        return f'{minutes} minute(s) and {seconds} second(s)'

    def _query_params_string(self, query_params={}):
        params = []
        for key, value in query_params.items():
            params.append(f'{key}={value}')
        if len(params) == 0:
            return ''
        return f'?{"&".join(params)}'

    def _set_is_rate_limited(self):
        self._current_requests = self._requests_per_hour * 1000
        self._next_reset_time = time.time() + (60 * 5)  # 5 minutes
        wait_response = ResponseItem(429, None)
        wait_response.is_rate_limited = True
        wait_response.wait_until = self._next_reset_time
        return wait_response

    def _send_request(self, resource_url, query_params={}, headers={}):
        if not self._check_current_limit():
            wait_response = ResponseItem(429, None)
            wait_response.is_rate_limited = True
            wait_response.wait_until = self._next_reset_time
            return wait_response

        self._current_requests = self._current_requests + 1
        response = requests.get(url=resource_url,
                                params=query_params,
                                headers=headers
                                )

        if response.status_code == 429:
            return self._set_is_rate_limited()

        if response.text:
            ret_data = json.loads(response.text)
        else:
            ret_data = None
        return ResponseItem(response.status_code, ret_data)

    def get_or_wait(self, resource_url, query_params={}, headers={}):
        self._logger.info(
            f'getting: {resource_url}{self._query_params_string(query_params)}')
        while True:
            response = self._send_request(
                resource_url, query_params=query_params, headers=headers)
            if response.is_rate_limited:
                wait_until_time = response.wait_until
                while time.time() < wait_until_time:
                    self._logger.info(
                        f'rate limit reached - waiting for {self._wait_time_delta(wait_until_time)}')
                    time.sleep(60)
                continue
            return response
