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

import threading
import json
import cherrypy

class ResultEndpoint:

    def __init__(self):
        self._result = None

    def set_result(self, result):
        self._result = result

    @cherrypy.expose
    def get_processing_result(self):
        return json.dumps(self._result)


class ResultEndpointServer(threading.Thread):
    def __init__(self, host: str="0.0.0.0", port: int=9333):
        super().__init__()
        self._host = host
        self._port = port

    def run(self):
        self._endpoint = ResultEndpoint()

        cherrypy.tree.mount(self._endpoint, '/')

        cherrypy.server.socket_host = self._host
        cherrypy.server.socket_port = self._port
        cherrypy.engine.autoreload.on = False
        cherrypy.engine.start()
        cherrypy.engine.block()

    def set_result(self, result):
        self._endpoint.set_result(result)
