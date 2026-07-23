from app.api.schemas.error_schema import ErrorBase

UNAUTHORIZED_RESPONSE = {
    "model": ErrorBase,
    "description": "Authentication required or the access token is invalid.",
}

FORBIDDEN_RESPONSE = {
    "model": ErrorBase,
    "description": "You do not have permission to perform this action.",
}

NOT_FOUND_RESPONSE = {
    "model": ErrorBase,
    "description": "The requested resource was not found.",
}

CONFLICT_RESPONSE = {
    "model": ErrorBase,
    "description": "The request could not be completed because the resource already exists or conflicts with the current state.",
}

BAD_REQUEST_RESPONSE = {
    "model": ErrorBase,
    "description": "The request is invalid.",
}

VALIDATION_ERROR_RESPONSE = {
    "description": "Validation Error",
}

INTERNAL_SERVER_ERROR_RESPONSE = {
    "model": ErrorBase,
    "description": "An unexpected internal server error occurred.",
}


AUTH_RESPONSES = {
    401: UNAUTHORIZED_RESPONSE,
}


PROTECTED_RESPONSES = {
    **AUTH_RESPONSES,
    403: FORBIDDEN_RESPONSE,
}

RESOURCE_RESPONSES = {
    **PROTECTED_RESPONSES,
    404: NOT_FOUND_RESPONSE,
}


CREATE_RESPONSES = {
    **PROTECTED_RESPONSES,
    409: CONFLICT_RESPONSE,
}


CREATE_RESOURCE_RESPONSES = {
    **RESOURCE_RESPONSES,
    409: CONFLICT_RESPONSE,
}


COMMON_RESPONSES = {
    400: BAD_REQUEST_RESPONSE,
    401: UNAUTHORIZED_RESPONSE,
    403: FORBIDDEN_RESPONSE,
    404: NOT_FOUND_RESPONSE,
    409: CONFLICT_RESPONSE,
    500: INTERNAL_SERVER_ERROR_RESPONSE,
}
