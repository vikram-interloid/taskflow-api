from fastapi import Request


def rate_limit_key(request: Request) -> str:

    if hasattr(request.state, "user"):
        user = request.state.user
    else:
        user = None

    if user:
        return f"user:{user.user_id}"

    return request.client.host
