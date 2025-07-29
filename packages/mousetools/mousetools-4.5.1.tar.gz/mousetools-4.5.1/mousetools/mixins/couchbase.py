import json
import logging
import re
from typing import Union

import requests

from mousetools.auth import auth_obj

logger = logging.getLogger(__name__)


class CouchbaseMixin:
    _couchbase_url = "https://" + auth_obj._environments["syncGatewayUrl"].split("//")[1].rstrip("/")
    _headers: dict = auth_obj.get_couchbase_headers()

    def get_channel_data(self, channel_name: Union[str, list[str]]) -> Union[list[dict], dict, None]:
        """
        Sends a request to the Disney Couchbase API with the given channel ID and returns the data.

        Args:
            channel_name (Union[str, list[str]]): Couchbase channel(s) to request data from.

        Returns:
            (Union[list[dict], dict, None]): The disney data.
        """

        if isinstance(channel_name, str):
            _channel_names = [channel_name]
            return_list = False
        else:
            _channel_names = channel_name
            return_list = True

        payload = {
            "docs": [{"id": name} for name in _channel_names],
            "json": True,
        }

        logger.info(
            "Sending request for channel data: %s", f"{len(channel_name)} channels" if return_list else _channel_names
        )
        response = requests.post(self._couchbase_url + "/_bulk_get", json=payload, headers=self._headers, timeout=10)
        logger.debug(
            "Response status for %s: %s",
            f"{len(channel_name)} channels" if return_list else _channel_names,
            response.status_code,
        )
        results = []
        try:
            response.raise_for_status()
            raw_data = response.text

            cont_reg = re.compile(r"\w+-\w+:\s\w+\/\w+")
            raw_data = re.sub(cont_reg, "", raw_data)
            raw_data = raw_data.splitlines()

            for line in raw_data:
                if line != "" and line[0] != "-":
                    try:
                        data = json.loads(line)
                        results.append(data)
                    except Exception:
                        logger.debug("Failed to parse line: %s", line)
                        continue
        except requests.HTTPError as err:
            logger.error("Request failed: %s", err)
            return None

        if return_list:
            return results
        else:
            return results[0]

    def get_channel_changes(
        self, channel_name: Union[str, list[str]], since: Union[int, None] = None
    ) -> Union[dict, None]:
        """Sends a request to the Disney Couchbase API with the given channel ID and returns the data.

        Args:
            channel_name (Union[str, list[str]]): Couchbase channel to request data from.
            since (Union[int, None], optional): Since when to get changes. Defaults to None.

        Returns:
            Union[dict, None]: The disney data.
        """

        if isinstance(channel_name, str):
            channel_name = [channel_name]

        try:
            payload = {
                "channels": ",".join(channel_name),
                "style": "all_docs",
                "filter": "sync_gateway/bychannel",
                "feed": "normal",
                "heartbeat": 30000,
            }
            if since:
                payload["since"] = since

            logger.info(
                "Sending request for channel changes: %s",
                f"{len(channel_name)} channels" if len(channel_name) > 1 else channel_name[0],
            )
            response = requests.post(self._couchbase_url + "/_changes", json=payload, headers=self._headers, timeout=10)
            logger.debug(
                "Response status for %s: %s",
                f"{len(channel_name)} channels" if len(channel_name) > 1 else channel_name[0],
                response.status_code,
            )
            response.raise_for_status()
            data = response.json()
        except requests.HTTPError as err:
            logger.error("Request failed: %s", err)
            return None

        return data
