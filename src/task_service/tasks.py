from celery.schedules import crontab
from celery import chain

from app.bootstrap import bootstrap_celery_app, bootstrap_db_session, bootstrap_handler


app = bootstrap_celery_app()


def get_db_session():
    db_session = bootstrap_db_session()
    try:
        yield db_session
    finally:
        db_session.remove()

def get_handler(db_session):
    handler = bootstrap_handler(db_session)
    return handler


app.conf.beat_schedule = {
    'fetch-every-minute': {
        'task': 'tasks.collect_actual_data',
        'schedule': crontab(minute='*')
    }
}

app.conf.timezone = 'UTC'


@app.task()
def aggregate_data(stock_id, interval, user_id):
    db_session = next(get_db_session())
    handler = get_handler(db_session)
    handler.aggregate_data(stock_id, interval, user_id)


@app.task()
def collect_actual_data():
    db_session = next(get_db_session())
    handler = get_handler(db_session)
    handler.collect_actual_data()


@app.task()
def collect_stocks():
    db_session = next(get_db_session())
    print(db_session)
    handler = get_handler(db_session)
    handler.collect_stock()


@app.task()
def collect_stock_data_example(data=None):
    print("start collect stock data")
    db_session = next(get_db_session())
    handler = get_handler(db_session)
    handler.collect_stock_data_example()


task_chain = chain(collect_stocks.s() | collect_stock_data_example.s())
# task_chain.delay()
