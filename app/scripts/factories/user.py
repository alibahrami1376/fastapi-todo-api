from faker import Faker
from models import UserModel

DEFAULT_TEST_PASSWORD = "Aa@123456"


class UserFactory:
    @staticmethod
    def create(
        faker: Faker,
        is_active: bool = True,
        is_verified: bool = True,
    ) -> UserModel:
        user = UserModel(
            username=UserModel.generate_random_username(),
            email=faker.unique.email(),
            is_active=is_active,
            is_verified=is_verified,
        )
        user.set_password(DEFAULT_TEST_PASSWORD)
        return user
