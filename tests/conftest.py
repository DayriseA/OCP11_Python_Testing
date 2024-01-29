import pytest
import multiprocessing

from server import app as flask_app


# scope="session" needed to work with the live_server fixture
@pytest.fixture(scope="session")
def app():
    """
    Since python 3.8 where they refactored multiprocessing module the line
    multiprocessing.set_start_method("fork") is needed to avoid the:
    'AttributeError: Can't pickle local object'

    But it seems that this workaround does not work on Windows and Mac...
    So for now we will not use the live_server fixture and instead have to start the
    server manually before running the tests.
    """
    flask_app.config["TESTING"] = True
    multiprocessing.set_start_method("fork")
    return flask_app


# not using the app fixture here and instead directly use flask_app because we
# want our client used for unit tests to keep the default function scope
@pytest.fixture
def client():
    flask_app.config.update({"TESTING": True})
    with flask_app.test_client() as client:
        yield client
