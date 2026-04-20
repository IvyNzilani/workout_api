from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, Workout, Exercise, WorkoutExercise
from schemas import (
    exercise_schema, exercises_schema,
    workout_schema, workouts_schema, workout_detail_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]        = "sqlite:///workout.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)


def get_or_404(model, record_id):
    return db.session.get(model, record_id)


def error(message, status=400):
    return jsonify({"error": message}), status


@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route("/workouts/<int:workout_id>", methods=["GET"])
def get_workout(workout_id):
    workout = get_or_404(Workout, workout_id)
    if not workout:
        return error(f"Workout {workout_id} not found.", 404)
    return jsonify(workout_detail_schema.dump(workout)), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    json_data = request.get_json()
    if not json_data:
        return error("Request body must be JSON.")
    try:
        data = workout_schema.load(json_data)
    except ValidationError as exc:
        return jsonify({"errors": exc.messages}), 400
    try:
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc))
    return jsonify(workout_schema.dump(workout)), 201


@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    workout = get_or_404(Workout, workout_id)
    if not workout:
        return error(f"Workout {workout_id} not found.", 404)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": f"Workout {workout_id} deleted."}), 200


@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route("/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    exercise = get_or_404(Exercise, exercise_id)
    if not exercise:
        return error(f"Exercise {exercise_id} not found.", 404)
    data = exercise_schema.dump(exercise)
    data["workouts"] = [w.to_dict() for w in exercise.workouts]
    return jsonify(data), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    json_data = request.get_json()
    if not json_data:
        return error("Request body must be JSON.")
    try:
        data = exercise_schema.load(json_data)
    except ValidationError as exc:
        return jsonify({"errors": exc.messages}), 400
    try:
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc))
    return jsonify(exercise_schema.dump(exercise)), 201


@app.route("/exercises/<int:exercise_id>", methods=["DELETE"])
def delete_exercise(exercise_id):
    exercise = get_or_404(Exercise, exercise_id)
    if not exercise:
        return error(f"Exercise {exercise_id} not found.", 404)
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": f"Exercise {exercise_id} deleted."}), 200


@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout  = get_or_404(Workout,  workout_id)
    exercise = get_or_404(Exercise, exercise_id)
    if not workout:
        return error(f"Workout {workout_id} not found.", 404)
    if not exercise:
        return error(f"Exercise {exercise_id} not found.", 404)
    json_data = request.get_json() or {}
    try:
        data = workout_exercise_schema.load(json_data)
    except ValidationError as exc:
        return jsonify({"errors": exc.messages}), 400
    try:
        we = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data.get("reps", 0),
            sets=data.get("sets", 0),
            duration_seconds=data.get("duration_seconds", 0),
        )
        db.session.add(we)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc))
    return jsonify(workout_exercise_schema.dump(we)), 201


if __name__ == "__main__":
    app.run(debug=True)
