import serverless_sdk
sdk = serverless_sdk.SDK(
    org_id='benmusch',
    application_name='letterboxd-slack',
    app_uid='6myCRvCMMhJp1Dn1pl',
    org_uid='xqbtrhtXNs8qrLZQDT',
    deployment_uid='63d4477a-fadf-42d8-8fb5-658dfb9af82a',
    service_name='letterboxd-slack-cron',
    should_log_meta=True,
    should_compress_logs=True,
    disable_aws_spans=False,
    disable_http_spans=False,
    stage_name='prod',
    plugin_version='4.3.0',
    disable_frameworks_instrumentation=False,
    serverless_platform_stage='prod'
)
handler_wrapper_kwargs = {'function_name': 'letterboxd-slack-cron-prod-cron', 'timeout': 6}
try:
    user_handler = serverless_sdk.get_user_handler('letterboxd_slack.main')
    handler = sdk.handler(user_handler, **handler_wrapper_kwargs)
except Exception as error:
    e = error
    def error_handler(event, context):
        raise e
    handler = sdk.handler(error_handler, **handler_wrapper_kwargs)
