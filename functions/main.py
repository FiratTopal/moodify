from firebase_admin import initialize_app
from firebase_functions import https_fn, options

initialize_app()

from app import app as flask_app

@https_fn.on_request(
    memory=options.MemoryOption.GB_2,
    timeout_sec=300,
    max_instances=1
)
def api(req: https_fn.Request) -> https_fn.Response:
    with flask_app.request_context(req.environ):
        return flask_app.full_dispatch_request()

