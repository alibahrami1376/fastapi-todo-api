REGISTER_RESPONSE_EXAMPLE = {
    "user_id": 1,
    "email": "user@example.com",
    "detail": "Your account has been created successfully.",
}

LOGIN_RESPONSE_EXAMPLE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
}

REFRESH_RESPONSE_EXAMPLE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
}

LOGOUT_RESPONSE_EXAMPLE = {
    "detail": "You have been logged out successfully.",
}

USER_RESPONSE_EXAMPLE = {
    "id": 1,
    "username": "johndoe123",
    "email": "user@example.com",
    "is_active": True,
    "is_verified": False,
    "created_date": "2026-08-19T10:00:00+03:30",
    "updated_date": "2026-08-19T10:00:00+03:30",
}

TASK_RESPONSE_EXAMPLE = {
    "id": 1,
    "title": "Finish project report",
    "description": "Complete the weekly status report",
    "is_completed": False,
    "priority": "high",
    "due_date": "2026-08-31",
    "owner_id": 1,
    "created_date": "2026-08-19T10:00:00+03:30",
    "updated_date": "2026-08-19T10:00:00+03:30",
}

TASK_LIST_RESPONSE_EXAMPLE = {
    "results": [TASK_RESPONSE_EXAMPLE],
    "page": 1,
    "page_size": 10,
    "total": 1,
    "pages": 1,
}

TASK_STATS_RESPONSE_EXAMPLE = {
    "total": 10,
    "completed": 4,
    "pending": 6,
    "overdue": 2,
    "by_priority": {
        "low": 3,
        "medium": 5,
        "high": 2,
    },
}
