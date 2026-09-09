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

from flask import Flask, request, jsonify
from .task_manager import task_manager

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.get("/ping")
def ping():
    return "PONG", 200


@app.post("/api/task/list")
def list_task():
    tasks = task_manager.list_tasks()
    return jsonify(tasks), 200


@app.post("/api/task/list/registry")
def list_task_re():
    tasks = task_manager.list_task_registry()
    return jsonify(tasks), 200


@app.post("/api/task/start")
def start_task():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body"}), 400

        task_type = data.get("task_type")
        input_data = data.get("input", {})

        if task_type is None:
            return jsonify({"error": "task_type is required"}), 400

        result = task_manager.start_task(task_type, input_data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@app.post("/api/task/status")
def get_task_status():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body"}), 400

        task_id = data.get("task_id")
        if not task_id:
            return jsonify({"error": "task_id is required"}), 400

        task_info = task_manager.get_task_info(task_id)
        if not task_info:
            return jsonify({"error": "Task not found"}), 404

        return jsonify(task_info), 200
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@app.post("/api/task/cancel")
def cancel_task():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body"}), 400
        task_id = data.get("task_id")
        success = task_manager.cancel_task(task_id)
        if success:
            return jsonify({"message": "Task cancelled"}), 200
        else:
            return jsonify({"error": "Task not found or cannot be cancelled"}), 404
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500
