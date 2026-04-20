from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE

VALID_CATEGORIES = ["Cardio", "Strength", "Flexibility", "Balance", "Mobility"]

class ExerciseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id                = fields.Int(dump_only=True)
    name              = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120, error="Name must be 1-120 characters.")
    )
    category          = fields.Str(
        required=True,
        validate=validate.OneOf(
            VALID_CATEGORIES,
            error=f"Category must be one of: {', '.join(VALID_CATEGORIES)}."
        )
    )
    equipment_needed = fields.Bool(load_default=False)

    @validates("name")
    def validate_name_no_digits_only(self, value):
        if value.strip().isdigit():
            raise ValidationError("Exercise name cannot be numeric only.")

class WorkoutExerciseSchema(Schema):
    id               = fields.Int(dump_only=True)
    reps             = fields.Int(validate=validate.Range(min=0))
    sets             = fields.Int(validate=validate.Range(min=0))
    duration_seconds = fields.Int(validate=validate.Range(min=0))
    exercise         = fields.Nested(ExerciseSchema, dump_only=True)

class WorkoutSchema(Schema):
    id               = fields.Int(dump_only=True)
    date             = fields.Date(required=True)
    duration_minutes = fields.Int(validate=validate.Range(min=1))
    notes            = fields.Str()

class WorkoutDetailSchema(WorkoutSchema):
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)

# Initialize schemas
exercise_schema         = ExerciseSchema()
exercises_schema        = ExerciseSchema(many=True)
workout_schema          = WorkoutSchema()
workouts_schema         = WorkoutSchema(many=True)
workout_detail_schema   = WorkoutDetailSchema()
workout_exercise_schema = WorkoutExerciseSchema()