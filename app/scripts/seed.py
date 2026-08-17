from faker import Faker
from app.scripts.factories.user import UserFactory,DEFAULT_TEST_PASSWORD
from app.scripts.factories.task import TaskFactory

from core.database import SessionLocal

def seed():
    faker = Faker()
    db = SessionLocal()
    try:
        user = UserFactory.create(faker)

        db.add(user)
        
        # Get user.id before creating tasks
        db.flush()
        print(user.id,user.email,DEFAULT_TEST_PASSWORD)
        # Create tasks
        tasks = TaskFactory.create(
            faker=faker,
            user=user,
        )

        db.add_all(tasks)

        db.commit()
    finally:
        print("finish crate data for test ")
        db.close()


if __name__ == "__main__":
    seed()