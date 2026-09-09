# Copyright 2026 InsightOS
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ability_py
import threading
from .server import app
from werkzeug.serving import make_server


class ServerThread(threading.Thread):
    def __init__(self, host="0.0.0.0", port=8080):
        super().__init__(daemon=True)
        self.server = make_server(host, port, app)

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class ImplAbility(ability_py.AbilityInterface):
    """EndpointControl.Robotics 能力实现"""

    def __init__(self):
        self.ability_port = 0
        self.st = None

    def on_start(self):
        # TODO: 初始化资源（如加载模型、连接设备等）
        pass

    def on_connect(self):
        if self.ability_port:
            return
        self.ability_port = ability_py.get_free_port()
        self.st = ServerThread(host="localhost", port=self.ability_port)
        self.st.start()

    def on_disconnect(self):
        if self.ability_port != 0:
            self.st.shutdown()
            self.ability_port = 0

    def on_terminate(self):
        # TODO: 释放资源
        pass

    def get_ability_port(self) -> int:
        return self.ability_port
