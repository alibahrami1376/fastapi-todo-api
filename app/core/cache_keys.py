def auth_session_key(jti: str) -> str:
    return f"auth:session:{jti}"


def auth_user_key(user_id: int) -> str:
    return f"auth:user:{user_id}"


def todos_stats_key(user_id: int) -> str:
    return f"todos:stats:{user_id}"


def todos_list_pattern(user_id: int) -> str:
    return f"todos:list:{user_id}:*"


def todos_detail_key(user_id: int, todo_id: int) -> str:
    return f"todos:detail:{user_id}:{todo_id}"
