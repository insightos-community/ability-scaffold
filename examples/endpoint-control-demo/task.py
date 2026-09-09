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

from service import TaskInterface


class MoveToPoseTask(TaskInterface):
    """移动末端到目标位姿 (taskType: 0)

    Args:
        input_data: {
            "position": Point3d,  # 目标位置 (x, y, z)，单位米
            "orientation": Quaternion,  # 目标姿态四元数 (x, y, z, w)
            "velocity_scale": float (optional),  # 速度缩放因子 (0.0~1.0)，默认 0.3
            "acceleration_scale": float (optional),  # 加速度缩放因子 (0.0~1.0)，默认 0.3
        }

    Returns:
        {
            "success": bool,  # 是否到达目标位姿
            "final_position": Point3d,  # 实际到达的位置
            "error_distance": float,  # 与目标位置的误差距离 (米)
        }
    """

    def execute(self, input_data: dict) -> dict:
        position = input_data.get("position", None)
        orientation = input_data.get("orientation", None)
        velocity_scale = input_data.get("velocity_scale", 0.0)
        acceleration_scale = input_data.get("acceleration_scale", 0.0)

        # TODO: 实现移动末端到目标位姿逻辑
        raise NotImplementedError("MoveToPoseTask.execute()")


class MoveAlongTrajectoryTask(TaskInterface):
    """沿笛卡尔轨迹移动末端 (taskType: 1)

    Args:
        input_data: {
            "waypoints": list,  # 路径点列表，每个元素包含 position 和 orientation
            "velocity_scale": float (optional),  # 速度缩放因子，默认 0.2
            "blend_radius": float (optional),  # 路径点间的混合半径 (米)，默认 0.01
        }

    Returns:
        {
            "success": bool,  # 是否完成轨迹跟踪
            "completed_waypoints": int,  # 已完成的路径点数量
            "total_waypoints": int,  # 总路径点数量
        }
    """

    def execute(self, input_data: dict) -> dict:
        waypoints = input_data.get("waypoints", [])
        velocity_scale = input_data.get("velocity_scale", 0.0)
        blend_radius = input_data.get("blend_radius", 0.0)

        # TODO: 实现沿笛卡尔轨迹移动末端逻辑
        raise NotImplementedError("MoveAlongTrajectoryTask.execute()")


class MoveJointsTask(TaskInterface):
    """关节空间运动到目标关节角度 (taskType: 2)

    Args:
        input_data: {
            "joint_positions": list,  # 目标关节角度列表 (弧度)
            "velocity_scale": float (optional),  # 速度缩放因子，默认 0.3
        }

    Returns:
        {
            "success": bool,  # 是否到达目标关节角度
            "final_joints": list,  # 实际到达的关节角度
        }
    """

    def execute(self, input_data: dict) -> dict:
        joint_positions = input_data.get("joint_positions", [])
        velocity_scale = input_data.get("velocity_scale", 0.0)

        # TODO: 实现关节空间运动到目标关节角度逻辑
        raise NotImplementedError("MoveJointsTask.execute()")


class SetGripperTask(TaskInterface):
    """控制夹爪开合 (taskType: 3)

    Args:
        input_data: {
            "opening": float,  # 夹爪开合度 (0.0=完全闭合, 1.0=完全张开)
            "force": float (optional),  # 夹持力 (N)，默认 10.0
            "speed": float (optional),  # 夹爪运动速度 (0.0~1.0)，默认 0.5
        }

    Returns:
        {
            "success": bool,  # 夹爪是否到达目标状态
            "actual_opening": float,  # 夹爪实际开合度
            "object_detected": bool,  # 是否检测到物体被夹持
        }
    """

    def execute(self, input_data: dict) -> dict:
        opening = input_data.get("opening", 0.0)
        force = input_data.get("force", 0.0)
        speed = input_data.get("speed", 0.0)

        # TODO: 实现控制夹爪开合逻辑
        raise NotImplementedError("SetGripperTask.execute()")


class GetCurrentPoseTask(TaskInterface):
    """获取末端当前位姿 (taskType: 4)

    Returns:
        {
            "position": Point3d,  # 当前末端位置
            "orientation": Quaternion,  # 当前末端姿态
            "joint_positions": list,  # 当前各关节角度
        }
    """

    def execute(self, input_data: dict) -> dict:
        # TODO: 实现获取末端当前位姿逻辑
        raise NotImplementedError("GetCurrentPoseTask.execute()")
