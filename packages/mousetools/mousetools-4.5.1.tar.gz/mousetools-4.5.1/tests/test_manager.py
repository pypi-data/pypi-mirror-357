from mousetools.channels.facilities import FacilityChannel, FacilityChildChannel
from mousetools.channels.facilities.enums import DLRCouchbaseChannels, WDWCouchbaseChannels
from mousetools.channels.manager import ChannelManager


def test_manager():
    channel_manager = ChannelManager([])
    assert channel_manager.get_channel_ids() == []

    wdw = FacilityChannel(WDWCouchbaseChannels.FACILITIES)
    dlr = FacilityChannel(DLRCouchbaseChannels.FACILITIES)
    channel_manager.add_channel(wdw)
    channel_manager.add_channel(dlr)
    assert channel_manager.get_all_channels() == [wdw, dlr]

    channel = channel_manager.remove_channel(WDWCouchbaseChannels.FACILITIES.value, return_channel=True)
    assert channel.channel_id == WDWCouchbaseChannels.FACILITIES.value
    assert len(channel_manager.get_all_channels()) == 1

    channel_manager.add_channel(
        FacilityChildChannel("wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction")
    )
    assert dlr._cb_data is None
    channel_manager.refresh()
    assert dlr._cb_data is not None

    channel = channel_manager.get_channel("wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction")
    assert channel.channel_id == "wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction"
