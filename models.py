from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()

VALID_CATEGORIES = ["Cardio", "Strength", "Flexibility", "Balance", "Mobility"]

class Exercise(db.Model):
    __tablename__ = "exercises"

    __table_args__ = (
        CheckConstraint("length(name) > 0", name="ck_exercise_name_nonempty"),
        CheckConstraint("category != ''",   name="ck_exercise_category_nonempty"),
    )

    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(120), nullable=False, unique=True)
    category          = db.Column(db.String(60),  nullable=False)
    equipment_needed  = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = db.relationship(
        "Workout", secondary="workout_exercises", back_populates="exercises", viewonly=True
    )

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be empty.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "equipment_needed": self.equipment_needed
        }

class Workout(db.Model):
    __tablename__ = "workouts"

    id               = db.Column(db.Integer, primary_key=True)
    date             = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer)
    notes            = db.Column(db.Text)

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = db.relationship(
        "Exercise", secondary="workout_exercises", back_populates="workouts", viewonly=True
    )

class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id               = db.Column(db.Integer, primary_key=True)
    workout_id       = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id      = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps             = db.Column(db.Integer)
    sets             = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout  = db.relationship("Workout",  back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")