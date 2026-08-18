import sys
from pathlib import Path

from dotenv import load_dotenv
from faker import Faker

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

load_dotenv(APP_DIR / ".env")

from core.database import SessionLocal

from scripts.factories.task import TaskFactory
from scripts.factories.user import DEFAULT_TEST_PASSWORD, UserFactory


def seed():
    faker = Faker()
    db = SessionLocal()

    print("\n🌱 Starting database seed...\n")

    try:
        # Create user
        user = UserFactory.create(faker)
        db.add(user)
        db.flush()

        print("👤 User created successfully")
        print(f"   ├─ ID:       {user.id}")
        print(f"   ├─ Username: {user.username}")
        print(f"   ├─ Email:    {user.email}")
        print(f"   └─ Password: {DEFAULT_TEST_PASSWORD}\n")

        # Create tasks
        tasks = TaskFactory.create(
            faker=faker,
            user=user,
        )

        db.add_all(tasks)

        print(f"📝 {len(tasks)} tasks created successfully")

        db.commit()

        print("\n✅ Database seed completed successfully!\n")

    except Exception:
        db.rollback()
        print("\n❌ Database seed failed. Transaction rolled back.\n")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
