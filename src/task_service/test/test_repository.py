from app.storage import StocksRepository
from tasks import get_db_session, get_handler
from pprint import pprint


def test_get_aggregation():
    session = next(get_db_session())
    handler = get_handler(session)

    repository = handler._repository
    result = repository.get_aggregation("", "1h")
    for i in result:
        pprint(i)


test_get_aggregation()
