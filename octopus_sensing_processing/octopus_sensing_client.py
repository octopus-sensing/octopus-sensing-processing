# This file is part of Octopus Sensing Processing <https://octopus-sensing.nastaran-saffar.me/>
# Copyright © 2022 Nastaran Saffaryazdi <nsaffar@gmail.com>
#
# Octopus Sensing Processing is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Octopus Sensing Processing is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Octopus Sensing
# Processing. If not, see <https://www.gnu.org/licenses/>.

import pickle
import urllib.request
import logging
import time
# The data received from the server might be in numpy format.
# We need to import 'numpy' to unpickle it.
from typing import Optional, List


class OctopusSensingClient:
    def __init__(self, host: str= "127.0.0.1", port: int=9330):
        self._host = host
        self._port = port

    def fetch(self, duration: int=3, device_list: str=None):
        if device_list is None:
            url = "http://{0}:{1}/?duration={2}".format(self._host, self._port, duration)
        else:
            # device_list can be like this "device1,device2"
            url = "http://{0}:{1}/?duration={2}&device_list={3}".format(self._host,
                                                                        self._port,
                                                                        duration,
                                                                        device_list)
        try:
            serialized_data = self.__request_data(url, retries=60)
        except Exception as error:
            raise error
        
        raw_data = pickle.loads(serialized_data)
        data = {}

        for key, device_data in raw_data.items():
            if device_data["metadata"]["type"] == "OpenBCIStreaming":
                data.setdefault("eeg", {})
                data["eeg"]["data"] = self._restructure_eeg(device_data["data"])
                data["eeg"]["sampling_rate"] = device_data["metadata"]["sampling_rate"]
                data["eeg"]["channels"] = device_data["metadata"]["channels"]

            if device_data["metadata"]["type"] == "BrainFlowOpenBCIStreaming":
                data.setdefault("eeg", {})
                data["eeg"]["data"] = self._restructure_eeg(device_data["data"])
                data["eeg"]["sampling_rate"] = device_data["metadata"]["sampling_rate"]
                data["eeg"]["channels"] = device_data["metadata"]["channels"]

            if device_data["metadata"]["type"] == "Shimmer3Streaming":
                data.setdefault("ppg", {})
                data.setdefault("gsr", {})
                gsr_records, ppg_records, = self._restructure_shimmer(device_data["data"])
                data["gsr"]["data"] = gsr_records
                data["ppg"]["data"] = ppg_records
                data["gsr"]["sampling_rate"] = device_data["metadata"]["sampling_rate"]
                data["ppg"]["sampling_rate"] = device_data["metadata"]["sampling_rate"]

            if device_data["metadata"]["type"] == "CameraStreaming":
                data.setdefault("camera", {})
                # The type of data is a list of numpy-array. Each item is a frame
                data["camera"]["data"] = device_data["data"]
                data["camera"]["frame_rate"] = device_data["metadata"]["frame_rate"]

        return data

    def __request_data(self, url, retries=60):
            try:
                request = urllib.request.Request(url,
                                                headers={"Accept": "application/pickle"},
                                                method='GET')
                with urllib.request.urlopen(request) as response:
                    if response.getcode() != 200:
                        raise RuntimeError("Getting data failed. Got HTTP status: {0} {1}".format(response.status,
                                                                                                  response.reason))
                        
                    serialized_data = response.read()
                    return serialized_data
            except Exception as err:
                if retries == 0:
                    logging.error(f"Failed to get the data: {err}")
                    raise
                else:
                    logging.error(f"Getting data failed. Re-trying [{retries}]. Error: {err}")
                    time.sleep(1)
                    return self.__request_data(url, retries=retries - 1)


    def _restructure_eeg(self, data):
        channels = 8
        if len(data[0]) >= 16:
            channels = 16

        result = []

        for _ in range(channels):
            result.append([])

        for record in data:
            for i, channel_data in enumerate(record[1:channels+1]):
                result[i].append(channel_data)

        return result

    def _restructure_shimmer(self, data):
        gsr_records = []
        ppg_records = []

        for record in data:
            gsr_records.append(record[5])
            ppg_records.append(record[6])

        return (gsr_records, ppg_records)

