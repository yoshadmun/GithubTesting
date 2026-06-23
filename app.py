"""
A basic REST API for managing a list of Tasks.

This uses Flask and an in-memory data store (a simple Python list), so you can
test all the endpoints without setting up a real database.

--------------------------------------------------------------------------
HOW TO RUN
--------------------------------------------------------------------------
1. Install Flask (one time):
       pip install flask

2. Start the server from this folder:
       python app.py

   The API runs at http://127.0.0.1:5000 by default.

3. Try the endpoints (examples using curl):
       # Get all tasks
       curl http://127.0.0.1:5000/tasks

       # Add a new task
       curl -X POST http://127.0.0.1:5000/tasks \
            -H "Content-Type: application/json" \
            -d "{\"title\": \"Buy milk\"}"

       # Update task with id 1
       curl -X PUT http://127.0.0.1:5000/tasks/1 \
            -H "Content-Type: application/json" \
            -d "{\"title\": \"Buy oat milk\", \"done\": true}"

       # Delete task with id 1
       curl -X DELETE http://127.0.0.1:5000/tasks/1
--------------------------------------------------------------------------
"""

from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# -------------------------------------------------------------------------
# In-memory data store.
# `tasks` holds our resources; `next_id` tracks the ID for the next new task.
# This data resets every time the server restarts (no database involved).
# -------------------------------------------------------------------------
tasks = [
    {"id": 1, "title": "Learn Flask", "done": False},
    {"id": 2, "title": "Build a REST API", "done": False},
]
next_id = 3


def find_task(task_id):
    """Return the task dict matching task_id, or None if it doesn't exist."""
    return next((task for task in tasks if task["id"] == task_id), None)


# -------------------------------------------------------------------------
# GET /tasks
# Fetch and return the full list of tasks.
# -------------------------------------------------------------------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200


# -------------------------------------------------------------------------
# GET /tasks/<id>
# Fetch a single task by its ID (handy for testing the other routes).
# -------------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = find_task(task_id)
    if task is None:
        abort(404, description="Task not found")
    return jsonify(task), 200


# -------------------------------------------------------------------------
# POST /tasks
# Add a new task. Expects JSON with at least a "title" field.
# Returns the newly created task and HTTP 201 (Created).
# -------------------------------------------------------------------------
@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id

    data = request.get_json(silent=True)
    if not data or "title" not in data:
        abort(400, description="Request must include a 'title' field")

    new_task = {
        "id": next_id,
        "title": data["title"],
        # "done" is optional; default to False if not provided.
        "done": bool(data.get("done", False)),
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


# -------------------------------------------------------------------------
# PUT /tasks/<id>
# Update an existing task by its ID. Any of "title" or "done" may be sent;
# fields that are omitted keep their current values.
# -------------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = find_task(task_id)
    if task is None:
        abort(404, description="Task not found")

    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be valid JSON")

    # Only overwrite fields that were actually provided.
    if "title" in data:
        task["title"] = data["title"]
    if "done" in data:
        task["done"] = bool(data["done"])

    return jsonify(task), 200


# -------------------------------------------------------------------------
# DELETE /tasks/<id>
# Remove a task by its ID.
# -------------------------------------------------------------------------
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = find_task(task_id)
    if task is None:
        abort(404, description="Task not found")

    tasks.remove(task)
    return jsonify({"message": f"Task {task_id} deleted"}), 200


# -------------------------------------------------------------------------
# Return JSON (instead of HTML) for common errors, so API clients get
# consistent, parseable responses.
# -------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error.description)}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error.description)}), 400


if __name__ == "__main__":
    # debug=True enables auto-reload and detailed errors during development.
    app.run(debug=True)
