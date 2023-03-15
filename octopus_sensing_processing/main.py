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

import time
import argparse

from octopus_sensing_processing.octopus_sensing_client import OctopusSensingClient

from octopus_sensing_processing.result_endpoint import ResultEndpointServer
from octopus_sensing_processing.result_streaming import ResultStreaming

def get_args():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-t", "--time",
                            help="The time duration of getting data in seconds.",
                            default=3,
                            type=int)

    arg_parser.add_argument("-d", "--devices",
                            help="The list of devices names (The names passed to device coordinator). It can be like this: device1,device2",
                            type=str,
                            required=True)
    arg_parser.add_argument("-s", "--streaming",
                            help="Stream the result. Example: http://127.0.0.1:9332/",
                            type=str)
    arg_parser.add_argument("-e", "--endpoint",
                            help="GET endpoint for the result. Example: 0.0.0.0:9333",
                            type=str)
    arg_parser.add_argument("-m", "--module",
                            help="The module containing the processor function.",
                            required=True)
    arg_parser.add_argument("-f", "--function",
                            help="The name of the processor function.",
                            required=True)
    return arg_parser.parse_args()


def main():
    args = get_args()

    processor_module = __import__(args.module, globals(), locals(), [args.function])
    processor = getattr(processor_module, args.function)

    client = OctopusSensingClient()

    if args.endpoint is not None:
        server_address = args.endpoint.split(":")
        if len(server_address) < 2:
            raise RuntimeError("The endpoint addrees is not in the correct format. It should be something like this: 0.0.0.0:9333")
        result_endpoint = ResultEndpointServer(host=server_address[0], port=int(server_address[1]))
        result_endpoint.start()

    if args.streaming is not None:
        result_streaming = ResultStreaming(url=args.streaming)
    while True:
        start = time.time()

        data = client.fetch(duration=args.time, device_list=args.devices)
        processing_result = processor(data)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4"),
        print(processing_result)
        print("octopus", processing_result)
        if args.streaming is not None:
            result_streaming.push_processing_result(processing_result)
        if args.endpoint is not None:
            result_endpoint.set_result(processing_result)

        end = time.time()
        computation_delay = end-start
        if computation_delay < args.time:
            time.sleep(args.time - computation_delay)

if __name__ == '__main__':
    main()
