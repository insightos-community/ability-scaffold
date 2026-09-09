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

import time
import random
from service import TaskInterface


class MoveToPoseTask(TaskInterface):
    """移动末端到目标位姿 (taskType: 0)"""

    def execute(self, input_data: dict) -> dict:
        position = input_data.get("position", {"x": 0.0, "y": 0.0, "z": 0.0})
        orientation = input_data.get("orientation", {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0})
        velocity_scale = input_data.get("velocity_scale", 0.3)
        acceleration_scale = input_data.get("acceleration_scale", 0.3)

        # mock: 模拟运动耗时
        move_time = 1.0 / max(velocity_scale, 0.01)
        time.sleep(min(move_time, 2.0))

        # mock: 在目标位置附近加一个小误差
        error = random.uniform(0.0001, 0.003)
        final_position = {
            "x": position.get("x", 0.0) + random.uniform(-error, error),
            "y": position.get("y", 0.0) + random.uniform(-error, error),
            "z": position.get("z", 0.0) + random.uniform(-error, error),
        }

        return {
            "success": True,
            "final_position": final_position,
            "error_distance": round(error, 6),
        }


class MoveAlongTrajectoryTask(TaskInterface):
    """沿笛卡尔轨迹移动末端 (taskType: 1)"""

    def execute(self, input_data: dict) -> dict:
        waypoints = input_data.get("waypoints", [])
        velocity_scale = input_data.get("velocity_scale", 0.2)
        blend_radius = input_data.get("blend_radius", 0.01)

        total = len(waypoints)
        if total == 0:
            return {
                "success": False,
                "completed_waypoints": 0,
                "total_waypoints": 0,
            }

        # mock: 逐点模拟
        for i in range(total):
            time.sleep(0.3 / max(velocity_scale, 0.01) * 0.1)

        return {
            "success": True,
            "completed_waypoints": total,
            "total_waypoints": total,
        }


class MoveJointsTask(TaskInterface):
    """关节空间运动到目标关节角度 (taskType: 2)"""

    def execute(self, input_data: dict) -> dict:
        joint_positions = input_data.get("joint_positions", [])
        velocity_scale = input_data.get("velocity_scale", 0.3)

        time.sleep(1.0 / max(velocity_scale, 0.01) * 0.5)

        # mock: 在目标角度附近加微小误差
        final_joints = [
            round(j + random.uniform(-0.001, 0.001), 6)
            for j in joint_positions
        ]

        return {
            "success": True,
            "final_joints": final_joints,
        }


class SetGripperTask(TaskInterface):
    """控制夹爪开合 (taskType: 3)"""

    def execute(self, input_data: dict) -> dict:
        opening = input_data.get("opening", 0.5)
        force = input_data.get("force", 10.0)
        speed = input_data.get("speed", 0.5)

        time.sleep(0.5 / max(speed, 0.01))

        # mock: 夹爪实际开合度略有偏差
        actual_opening = round(min(max(opening + random.uniform(-0.02, 0.02), 0.0), 1.0), 4)
        # mock: 开合度 < 0.3 时有概率检测到物体
        object_detected = actual_opening < 0.3 and random.random() > 0.3

        return {
            "success": True,
            "actual_opening": actual_opening,
            "object_detected": object_detected,
        }


class GetCurrentPoseTask(TaskInterface):
    """获取末端当前位姿 (taskType: 4)"""

    def execute(self, input_data: dict) -> dict:
        return {
            "position": {
                "x": round(random.uniform(0.3, 0.6), 4),
                "y": round(random.uniform(-0.2, 0.2), 4),
                "z": round(random.uniform(0.1, 0.5), 4),
            },
            "orientation": {
                "x": 0.0,
                "y": round(random.uniform(0.6, 0.75), 4),
                "z": 0.0,
                "w": round(random.uniform(0.65, 0.8), 4),
            },
            "joint_positions": [
                round(random.uniform(-3.14, 3.14), 4)
                for _ in range(6)
            ],
        }
