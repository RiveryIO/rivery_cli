import logging
import zlib

import requests

from .utils import bson_utils as json_util, utils

MAX_PULL_TIME = 1800
SLEEP_PULL_TIME = 5
REQUEST_CONNECT_TIMEOUT = 20
REQUEST_READ_TIMEOUT = 180


class RiverySession(object):
    """
    Support class to work with the Rivery API
    """

    CONNECTION_TYPES = set()

    def __init__(self, *args, **kwargs):
        self.session = requests.session()
        self.access_token = kwargs.get('token') or kwargs.get('access_token')
        print(f'Host: {kwargs.get("host")}')
        self.account_id = None
        self.env_id = None
        self.host = kwargs.get("host") + "/api"

    def __repr__(self):
        return f"<RiverySession host:{self.host}>"

    def __str__(self):
        return f"<RiverySession host:{self.host}>"

    @property
    def headers(self):
        return {"Authorization": f'Bearer {self.access_token}'}

    def connect(self):
        """ Make a connection test """
        url = '/me'
        resp = self.handle_request(url=url)
        self.account_id = resp.get('account_id')
        self.env_id = resp.get('environment_id')

    @property
    def account(self):
        """ Set the account id in cli for the session, as come from the token """
        return self.account_id

    @property
    def environment_id(self):
        return self.env_id

    def send_request(self, url, method=None, params=None, headers=None, data=None, **kwargs):
        logging.debug("Send request started")
        logging.debug("sending {} request to {} with params {} and headers: {}".format(method, url, params, headers))
        headers.update(self.headers)
        try:
            timeout = (REQUEST_CONNECT_TIMEOUT, REQUEST_READ_TIMEOUT)
            if data:
                data = zlib.compress(json_util.dumps(data).encode("utf-8")) if headers.get("Content-Encoding",
                                                                                           "") == "gzip" else \
                    json_util.dumps(data)
            if method.lower() == "post":
                response = self.session.post(url=url, params=params, timeout=timeout, data=data, headers=headers)
                return response

            if method.lower() == "get":
                response = self.session.get(url=url, params=params, headers=headers, timeout=timeout)
                return response

            if method.lower() == "delete":
                response = self.session.delete(url=url, params=params, data=data, headers=headers, timeout=timeout)
                return response

            if method.lower() == "patch":
                response = self.session.patch(url=url, data=data, params=params, headers=headers, timeout=timeout)
                return response

            if method.lower() == "put":
                response = self.session.put(url=url, data=data, params=params, headers=headers, timeout=timeout)
                return response

        except Exception as e:
            logging.error("Got an error from the API with: {}".format(str(e)))
            raise e

    def handle_request(self, url, method='get', params=None, headers=None, **kwargs):
        if headers is None:
            headers = {}
        logging.debug('handle_request started')
        resp = self.send_request(url=self.host + url, method=method, params=params, headers=headers, **kwargs)
        if resp.ok:
            if kwargs.get("return_full_response", False):
                return resp
            else:
                try:
                    return json_util.loads(resp.content)
                except Exception as e:
                    raise requests.HTTPError("Failed")

        elif not resp.ok and resp.content:
            try:
                error_msg = json_util.loads(resp.content)
            except Exception as e:
                error_msg = resp.content
                pass
            logging.error("Error from Rivery API: {}-{}".format(resp.status_code, error_msg))
            if isinstance(error_msg, dict):
                error_msg = error_msg.get("message", "")
            if 400 <= resp.status_code < 500:
                raise Exception(
                    "Permissions Error in Rivery API "
                    "Please check your credentials and permissions. API Error: {}".format(error_msg))
            elif resp.status_code >= 500:
                raise requests.HTTPError("Internal server error, "
                                         "see following error and try again later. API Error: {}".format(error_msg))
            else:
                raise Exception(
                    "Unknown error from Rivery API")
        else:
            logging.error("Received an error from Rivery API")
            raise Exception("Received an error from Rivery API")

    def list_rivers(self, **params):
        """ List the rivers """
        url_ = '/rivers/list'
        river_id = params.pop('river_id', None)
        if river_id:
            url_ = f'/rivers/{river_id}'
        return self.handle_request(url=url_, method='get', params=params)

    def get_river(self, **kwargs):
        """ Get specific river data """
        url = '/rivers/list'
        data = {"_id": kwargs.get('river_id') or kwargs.get('_id')}
        method = 'post'
        return self.handle_request(url=url, data=data, method=method)

    def get_connection(self, **kwargs):
        """ Get specific connection. required `_id` as the connection id"""
        url = f'/connections/{kwargs.get("_id")}'
        method = 'get'
        return self.handle_request(url=url, method=method)

    def list_connections(self, **kwargs):
        """ Get list of the availabe connection in this environment/account.
            The function can get "connection_type" parameter, which will filter
            the connections returns by connection type.
        """
        connection_type = kwargs.get('connection_type')
        url = "/connections/list"
        method = 'get'

        if not self.CONNECTION_TYPES:
            self.list_connection_types()

        if connection_type:
            if connection_type not in self.CONNECTION_TYPES:
                raise AssertionError(f'Invalid Connection Type: {connection_type}')

            url = f'/connections/{connection_type}'

        return self.handle_request(url=url, method=method)

    def list_connection_types(self):
        """ list the connection types, and populates the CONNECTION_TYPES parameter"""
        url = '/connection_types'
        resp = self.handle_request(url=url)
        self.CONNECTION_TYPES = {
            c.get('connection_type') for c in resp
        }
        return resp

    def get_connection_type_properties(self, connection_type):
        if connection_type not in self.CONNECTION_TYPES:
            return {}

        url = f'/connection_types/{connection_type}'
        return self.handle_request(url=url)

    def save_river(self, **kwargs):
        """ Save a new river, or update one
            :param create_new: Force new river with the specification of the data.
            :param river_definition: The data is
        """
        data = kwargs.get('data', {})

        payload = {"river_definitions": data.get("river_definitions"),
                   "tasks_definitions": data.get("tasks_definitions")}
        url = "/rivers/modify"
        if kwargs.get("create_new", False) or not data.get('cross_id'):
            logging.debug('Creating New River: {}({})'.format(
                data.get('river_definitions', {}).get('river_name'), data.get('cross_id')))
            method = "put"
        else:
            method = "patch"
            logging.debug('Checking out if the river {}({}) exists in the account and environment'.format(
                data.get('river_definitions', {}).get('river_name'), data.get('cross_id')
            ))
            exists = self.handle_request(url='/rivers/list', data={"_id": data.get('cross_id')},
                                         method='post')
            if not exists:
                logging.debug('river {}({}) does not exist. Create it. '.format(
                    data.get('river_definitions', {}).get('river_name'), data.get('cross_id')
                ))
                method = 'put'
            else:
                data['_id'] = exists.get('_id')
                data['cross_id'] = exists.get('cross_id')
                if not data.get('cross_id'):
                    raise RuntimeError('Please provide cross_id and cross_id to update river')
                existing_tasks = exists.get('tasks_definitions', [])
                for idx_, t in enumerate(payload.get('tasks_definitions', [])):
                    task_ = existing_tasks[idx_:idx_ + 1]
                    if task_:
                        payload['tasks_definitions'][idx_] = utils.recursive_update(task_[0], t)
                    else:
                        payload['tasks_definitions'][idx_] = t

                # Check if the river already exist by the id or not
            payload.update({"cross_id": data.get("cross_id"),
                            "_id": data.get("_id")})

        # headers = {"Content-Encoding": "gzip"}
        logging.debug(
            'Saving River {}({}). Creating New? {}'.format(data.get('river_definitions', {}).get('river_name'),
                                                           data.get('cross_id'),
                                                           True if method == 'put' else False))
        return self.handle_request(url=url, method=method, data=payload)

    def save_connection(self, **kwargs):
        """ Save a connection in Rivery """
        create_new = kwargs.pop('create_new', True)
        if create_new:
            self.create_connection(**kwargs)
        else:
            self.create_connection(**kwargs)

    def save_river_group(self, **kwargs):
        """ Create new river group """
        data = kwargs.get("data")
        url = "/river_groups"
        method = "put"
        return self.handle_request(url=url, method=method, data=data)

    def update_river_group(self, **kwargs):
        """ Update a river group """
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/river_groups"
        method = "patch"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def create_connection(self, **kwargs):
        """ Save new connection """
        data = kwargs.get("data")
        url = "/connections/create/data"
        method = "put"
        return self.handle_request(url=url, method=method, data=data)

    def update_connection(self, **kwargs):
        """ Update connection """
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/connections"
        method = "patch"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def delete_connection(self, **kwargs):
        """ Delete Connection """
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/connections"
        method = "delete"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def update_variable(self, **kwargs):
        """ Update Variable in the system """
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/environments/update_variable"
        method = "patch"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def pull_request(self, **kwargs):
        """ Run pull request mechanism """
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/pull/" + kwargs.get("url", "")
        method = "put" or kwargs.get("method", "put")
        return self.handle_request(url=url, method=method, data=data, params=params)

    def check_pull_request(self, **kwargs):
        """ Check pull request response """
        data = {}
        params = {"id": kwargs.get("id")}
        url = "/pull"
        method = "get"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def snapshot_versions_by_deploy(self, **kwargs):
        data = kwargs.get("data")
        params = kwargs.get("params")
        path_params = kwargs.get("path_params", [])
        url = ("/rivers/versions/snapshot/" if kwargs.get("is_river", True) else "/river_groups/versions/snapshot/") + \
              "/".join(path_params)
        method = "post"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def delete_river(self, **kwargs):
        """ Delete a river"""
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/rivers/modify"
        method = "delete"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def delete_group(self, **kwargs):
        """ Delete a group """
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/river_groups"
        method = "delete"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def restore_snapshot(self, **kwargs):
        """ restore snnapshot """
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/rivers/restore"
        method = "post"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def restore_snapshot_river_groups(self, **kwargs):
        data = kwargs.get("data")
        params = kwargs.get("params")
        url = "/river_groups/version/restore"
        method = "post"
        return self.handle_request(url=url, method=method, data=data, params=params)

    def cancel_run(self, **kwargs):
        """ Cancel specific run """
        data = kwargs.get("data")
        url = "/run/cancel"
        method = "post"
        return self.handle_request(url=url, method=method, data=data)

    def run_river(self, **kwargs):
        river_id = kwargs.get('river_id')
        url = '/run'
        method = 'post'
        data = {"river_id": river_id}
        return self.handle_request(url=url, method=method, data=data)

    def check_run(self, **kwargs):
        run_id = kwargs.get('run_id')
        url = '/check_run'
        method = 'get'
        param = {"run_id": run_id}
        return self.handle_request(url=url, method=method, params=param)

    def fetch_run_logs(self, **kwargs):
        return_full_response = kwargs.get('return_full_response')
        run_id = kwargs.get('run_id')
        url = '/activities/runs/logs'
        method = 'get'
        param = {"id": run_id}

        # Add query id if exists
        query_id = kwargs.get('query_id')
        if query_id:
            param["queryId"] = query_id

        response = self.handle_request(url=url, method=method, params=param,
                                       return_full_response=return_full_response)
        return response

    @staticmethod
    def _dumps(obj, **kwargs):
        """ Dumping an object to json using the json utils """
        return json_util.dumps(obj, **kwargs)

    @staticmethod
    def _dump(f_obj, obj, **kwargs):
        """ Dumping to file using json utils"""
        f_obj.write(json_util.dumps(obj, **kwargs))

    @staticmethod
    def _loads(stream, **kwargs):
        """ Loads a stream to json using json utils"""
        return json_util.loads(stream, **kwargs)

    @staticmethod
    def _load(f_obj, **kwargs):
        """Load from file using json util"""
        stream = f_obj.read()
        if stream:
            obj = json_util.loads(stream, **kwargs)
        else:
            obj = {}
        return obj

    def object_hook(self, dct):
        """ Update ObjectId Object Hook for requesting and responding """
        newdct = {}
        for k, v in dct.items():
            if (isinstance(v, str) or isinstance(v, bytes)) and len(v) == 12:
                newdct[k] = json_util.convert_oid(v)
            else:
                newdct[k] = v
        return newdct
