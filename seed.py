from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise

def seed():
    with app.app_context():
        print("Clearing existing data...")
        db.session.query(WorkoutExercise).delete()
        db.session.query(Workout).delete()
        db.session.query(Exercise).delete()
        db.session.commit()

        print("Seeding exercises...")
        ex1 = Exercise(name="Barbell Squat", category="Strength", equipment_needed=True)
        ex2 = Exercise(name="Push-Up", category="Strength", equipment_needed=False)
        db.session.add_all([ex1, ex2])
        db.session.commit()

        print("Seeding workouts...")
        w1 = Workout(date=date(2026, 4, 1), duration_minutes=60, notes="Morning session")
        db.session.add(w1)
        db.session.commit()

        print(f"Success! Created Workout ID: {w1.id} and Exercise ID: {ex2.id}")

if __name__ == "__main__":
    seed()