import logging
from typing import Optional, Union

from more_itertools import batched

from mousetools.channels import CouchbaseChannel, CouchbaseChildChannel
from mousetools.mixins.couchbase import CouchbaseMixin

logger = logging.getLogger(__name__)


class ChannelManager(CouchbaseMixin):
    def __init__(self, channels: list[Union[CouchbaseChannel, CouchbaseChildChannel]]) -> None:
        self._channel_store = {}
        for channel in channels:
            self._channel_store[channel.channel_id] = channel

    def add_channel(self, channel: Union[CouchbaseChannel, CouchbaseChildChannel]) -> None:
        """Adds a channel to the manager

        Args:
            channel (Union[CouchbaseChannel, CouchbaseChildChannel]): Channel to add
        """
        self._channel_store[channel.channel_id] = channel

    def get_channel(self, channel_id: str) -> Union[CouchbaseChannel, CouchbaseChildChannel]:
        """Returns a channel from the manager

        Args:
            channel_id (str): Channel ID

        Returns:
            Union[CouchbaseChannel, CouchbaseChildChannel]: The channel
        """
        return self._channel_store[channel_id]

    def get_all_channels(self) -> list[Union[CouchbaseChannel, CouchbaseChildChannel]]:
        """Returns a list of all channels in the manager

        Returns:
            list[Union[CouchbaseChannel, CouchbaseChildChannel]]: List of channels
        """
        return list(self._channel_store.values())

    def get_channel_ids(self) -> list[str]:
        """Returns a list of all channel ids in the manager

        Returns:
            list[str]: List of channel ids
        """
        return list(self._channel_store.keys())

    def remove_channel(
        self, channel_id: str, return_channel: bool = False
    ) -> Optional[Union[CouchbaseChannel, CouchbaseChildChannel]]:
        """Removes a channel from the manager

        Args:
            channel_id (str): Channel ID
            return_channel (bool, optional): If True, will return the channel. Defaults to False.

        Returns:
            Optional[Union[CouchbaseChannel, CouchbaseChildChannel]]: The channel
        """
        channel = self._channel_store.pop(channel_id)
        if return_channel:
            return channel

    def refresh(self) -> None:
        """Refreshes all channels in the manager

        Raises:
            ValueError: If the channel is not a child or parent channel
        """
        children_channels: dict[str, CouchbaseChildChannel] = {}
        parent_channels: dict[str, CouchbaseChannel] = {}

        for channel_id, channel in self._channel_store.items():
            if isinstance(channel, CouchbaseChildChannel):
                children_channels[channel_id] = channel
            elif isinstance(channel, CouchbaseChannel):
                parent_channels[channel_id] = channel
            else:
                raise ValueError(f"Channel {channel} is not a child or parent channel")
        logger.info(
            "Refreshing %d children channels and %d parent channels", len(children_channels), len(parent_channels)
        )

        self._refresh_children(children_channels)

        self._refresh_parents(parent_channels)

    def _refresh_children(self, children_channels: dict[str, CouchbaseChildChannel]) -> None:
        if children_channels:
            logger.debug("Refreshing children channels")
            for _channels in batched(children_channels, 100):
                children_results = self.get_channel_data(_channels)
                for channel_id, result in zip(_channels, children_results):
                    children_channels[channel_id]._refresh_from_manager(result)

    def _refresh_parents(self, parent_channels: dict[str, CouchbaseChannel]) -> None:
        if parent_channels:
            logger.debug("Refreshing parent channels")
            for _channels in batched(parent_channels, 100):
                parent_results = self.get_channel_changes(_channels)
                for channel_id in _channels:
                    copy_results = parent_results.copy()
                    new_results = []
                    for result in copy_results["results"]:
                        if channel_id in result["id"]:
                            new_results.append(result)
                    copy_results["results"] = new_results
                    parent_channels[channel_id]._refresh_from_manager(copy_results)
