from faker import Faker

from models import TaskModel, UserModel, PriorityTypes

COUNT_CREATE_TASK = 10


class TaskFactory:

    @staticmethod
    def create(
        faker: Faker,
        user: UserModel,
    ) -> list[TaskModel]:

        tasks = []

        for _ in range(COUNT_CREATE_TASK):
            task = TaskModel(
                title=faker.sentence(nb_words=7),
                description=faker.paragraph(nb_sentences=1),
                is_completed=faker.boolean(),
                priority=faker.random_element(
                    elements=list(PriorityTypes)
                ),
                due_date=faker.date_between(
                    start_date="today",
                    end_date="+30d",
                ),
                owner_id=user.id,
            )

            tasks.append(task)

        return tasks
