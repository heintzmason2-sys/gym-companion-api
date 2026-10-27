# 10/17/26 >># 10/17/26 >> Fixed Duplicate IDs with a separate counter
## used Global Counter removed lens + 1
# 10/17/26 >> Added Helper Function to remove redundant work with GET-ID, POST, Delete
# Validate before updating in PUT

from flask import Flask, jsonify, request
from flasgger import Swagger
app = Flask(__name__)
swagger = Swagger(app)

@app.errorhandler(404)
def err_hand_one(error):
    return jsonify({
        "error": "not_found",
        "message": "Requested resource not found"
    }), 404

@app.errorhandler(405)
def err_hand_two(error):
    return jsonify({
        "error": "method_not_allowed",
        "message": "Method not allowed for this resource",
    }), 405

workout_data = {
    "push": {
        "name": "Push Workout",
        "muscles": ["Chest", "Shoulders", "Triceps"],
        "exercises": [
            "Bench Press",
            "Overhead Press",
            "Cable Lateral Raise",
            "Triceps Pushdown"
        ]
    },
    "pull":{
        "name": "Pull Workout",
        "muscles": ["Back", "Biceps", "Rear-Delts"],
        "exercises": [
            "Lat Pulldown",
            "Barbell Row",
            "Face Pull",
            "Bicep Curl"
        ]
    },
    "leg": {
        "name": "Leg Workout",
        "muscles": ["Quads", "Hamstrings", "Calves", "Glutes"],
        "exercises": [
            "Barbell Back Squat",
            "Leg Press",
            "RDL",
            "Hip Thrust",
            "Calf Raises"
        ]
    }
}
# Stores workout logs in memory
workout_logs = []

# Tracks the next available workout log ID
next_log_id = 1

# Finds a workout log by its ID
def find_workout_log(log_id):
    for log in workout_logs:
        if log["id"] == log_id:
            return log
    return None

def validate_request_data():
    data = request.get_json(silent=True)
    if not isinstance(data,dict):
        return None
    
    return data

@app.route('/')
def home():
    print("Someone visited the GYM Companion API")
    return "Welcome to Gym Companion"

@app.route('/about')
def about():
    return "About Page"

@app.route("/workouts")
def workouts():
    return "Gym Companion Workouts"

@app.route('/workouts/push')
def push_workout():
    return jsonify({
        "name": workout_data["push"]["name"],
        "exercises": workout_data["push"]["exercises"]
    })

@app.route('/workouts/pull')
def pull_workout():
    return jsonify({
        "name": workout_data["pull"]["name"],
        "exercises": workout_data["pull"]["exercises"]
    })

@app.route('/workouts/leg')
def leg_workout():
    return jsonify({
        "name": workout_data["leg"]["name"],
        "exercises": workout_data["leg"]["exercises"]
    })

@app.route('/workouts/<workout_type>')
def get_workout(workout_type):
    if workout_type in workout_data:
        return jsonify({
            "name": workout_data[workout_type]["name"],
            "exercises": workout_data[workout_type]["exercises"]
        })
    else:
        return jsonify({"error": "Workout not found"}), 404


@app.route('/workout-logs', methods=['GET'])
def get_workout_logs():
    workout_type = request.args.get("workout_type")
    if workout_type:
        filtered_logs = [
            log for log in workout_logs
            if log["workout_type"] == workout_type
        ]
        return jsonify(filtered_logs)
    return jsonify(workout_logs)

@app.route('/workout-logs/<int:log_id>', methods=["GET"])
def get_workout_log(log_id):
    # Find the requested workout log
    log = find_workout_log(log_id)

    # Return the log if it exists
    if log is not None:
        return jsonify(log), 200
    # Return an error if the log doesn't exist
    return jsonify({"error": "Workout log not found"}), 404


@app.route('/workout-logs', methods=['POST'])
def create_workout_log():
    """
    Create Workout Log
    ---
    summary: Create a Workout Log.
    description: Creates a workout log.

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - workout_type
            - date
            - duration
            - notes
          properties:
            workout_type:
              type: string
              enum: [push, pull, leg]
            date:
              type: string
              format: date
            duration:
              type: integer
            notes:
              type: string

    responses:
      201:
        description: Workout log created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            workout_type:
              type: string
            date:
              type: string
              format: date
            duration:
              type: integer
            notes:
              type: string
      400:
        description: Invalid request data
        schema:
          type: object
          properties:
            error:
              type: string
    """
    global next_log_id

    data = validate_request_data()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    required_fields = ["workout_type", "date", "duration", "notes"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    if data["workout_type"] not in workout_data:
        return jsonify({"error": "Invalid workout type"}), 400

    workout_log = {
        "id": next_log_id,
        "workout_type": data["workout_type"],
        "date": data["date"],
        "duration": data["duration"],
        "notes": data["notes"]
    }

    workout_logs.append(workout_log)
    next_log_id += 1

    return jsonify(workout_log), 201


@app.route('/workout-logs/<int:log_id>', methods=['DELETE'])
def delete_workout_log(log_id):
    log = find_workout_log(log_id)

    if log is not None:
        workout_logs.remove(log)
        return jsonify({"message": "Workout log deleted"}), 200
    return jsonify({"error": "Workout log not found"}), 404

@app.route('/workout-logs/<int:log_id>', methods=['PUT'])
def update_workout_log(log_id):
    # Retrieve and validate the request body
    data = validate_request_data()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400
    # Find the requested workout log
    log = find_workout_log(log_id)
    
    if log is not None:
        if "workout_type" in data:
            if data["workout_type"] not in workout_data:
                return jsonify({"error": "Invalid workout type"}),400
        log["duration"] = data.get("duration", log["duration"])
        log["notes"] = data.get("notes", log["notes"])
        log["date"] = data.get("date", log["date"])
        
        # Update workout type if provided
        if "workout_type" in data:
            log["workout_type"] = data["workout_type"]
        return jsonify(log), 200
    return jsonify({"error": "Workout log not found"}), 404

@app.route("/workout-logs/stats", methods=["GET"])
def get_stats():
    total_workouts = len(workout_logs)
    total_duration = sum(log["duration"] for log in workout_logs)
    average = total_duration / total_workouts if total_workouts > 0 else 0
    
    return jsonify({
        "total_workouts": total_workouts,
        "total_duration": total_duration,
        "average_duration": average
    }), 200


if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True) 