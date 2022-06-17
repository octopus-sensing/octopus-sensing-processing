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

import cherrypy

class ResultEndpoint:

    def __init__(self):
        self._result = None

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
        print(cherrypy.request.json)


def main():
    endpoint = ResultEndpoint()

    cherrypy.tree.mount(endpoint, '/')

    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 9332
    cherrypy.engine.autoreload.on = False
    cherrypy.engine.start()
    cherrypy.engine.block()

main()
