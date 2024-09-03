import bootstrap as bts
from entrypoint import Entrypoint


def run():
    engine = bts.bootstrap_database_engine()
    auth_handler = bts.bootstrap_auth_handler(engine)

    gateway_service, app = bts.bootstrap_gateway_service()
    message_consumer_service = bts.bootstrap_message_consumer_service()
    data_sync_service = bts.bootstrap_data_sync_service()

    websocket_manager = bts.bootstrap_websocket_manager()
    worker_manager = bts.bootstrap_celery_worker_manager()
    actual_data_manager = bts.bootstrap_actual_data_manager()

    message_processor = bts.bootstrap_message_processor(
        websocket_manager,
        worker_manager,
        actual_data_manager
    )

    message_processor.register_service_callback(message_consumer_service, "send_message_to_client")
    message_processor.register_service_callback(data_sync_service, "sync_data", "collect_stocks")


    app.state.websocket_manager = websocket_manager
    app.state.auth_handler = auth_handler

    entrypoint = Entrypoint(
        [
            gateway_service,
            message_consumer_service,
            data_sync_service
        ],
        message_processor
    )


    with entrypoint as loop:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            exit(0)


if __name__ == "__main__":
    run()
