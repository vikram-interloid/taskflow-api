from fastapi import Request


def rate_limit_key(request: Request) -> str:
    user = getattr(request.state, "user", None)

    if user:
        return f"user:{user.user_id}"

    return request.client.host