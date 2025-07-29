import logging
from typing import Annotated

import uvicorn
from extratools_api.crudl import add_crudl_endpoints_for_mapping
from fastapi import Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from extratools_cloud.aws.sqs import get_resource_dict as get_sqs_resource_dict
from extratools_cloud.github.user import get_username

app = FastAPI(debug=True)

token_auth = HTTPBearer(auto_error=False)


add_crudl_endpoints_for_mapping(
    app,
    "/aws/sqs",
    get_sqs_resource_dict(json_only=True),
    values_in_list=True,
)


@app.get("/github/username")
async def get_github_username(
    token: Annotated[HTTPAuthorizationCredentials, Depends(token_auth)],
) -> str | None:
    try:
        return get_username(token.credentials) if token else None
    except RuntimeError:
        return None


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level=logging.DEBUG,
    )
