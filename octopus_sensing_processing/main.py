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
import datetime

from octopus_sensing_processing.octopus_sensing_client import OctopusSensingClient

from octopus_sensing_processing.result_endpoint import ResultEndpointServer
from octopus_sensing_processing.result_streaming import ResultStreaming

def get_args():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-d", "--duration",
                            help="duration of getting data in seconds",
                            default=3,
                            type=int)
    arg_parser.add_argument("-s", "--streaming",
                            help="Stream the result.",
                            default=False,
                            type=bool)
    arg_parser.add_argument("-r", "--request",
                            help="request the result.",
                            default=True,
                            type=bool)
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

    if args.request is True:
        result_endpoint = ResultEndpointServer()
        result_endpoint.start()

    if args.streaming is True:
        result_streaming = ResultStreaming()
    while True:
        start = time.time()
        data = client.fetch(duration=args.duration, device_list=["camera"])
        processing_result = processor(data)
        if args.streaming is True:
            result_streaming.push_processing_result(processing_result)
        if args.request is True:
            result_endpoint.set_result(processing_result)

        end = time.time()
        computation_delay = end-start
        if computation_delay < args.duration:
            time.sleep(args.duration - computation_delay)

if __name__ == '__main__':
    main()
