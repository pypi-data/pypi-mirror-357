from kitx.lib_logging import logger, LoggerInitializer, ObServe, ObserveConfig


async def run_all_tests():
    # example 1
    logger.info("-----------")
    # example 2  自动发送日志平台
    logger2 = LoggerInitializer(ObServe(ObserveConfig(
        observe_host='172.20.0.2',
        observe_port=40000,
        observe_base_dir="/logs",
        observe_username='root@example.com',
        observe_password='123456',
        observe_organization="algo_handwriting_database",  # 项目名
        observe_stream="dev"  # 环境+版本等
    ))).init_log()
    logger2.info("hhhh")
    await asyncio.sleep(1)  # await async


async def run_FastApi_test():
    from typing import Dict

    def my_filter2(log: Dict):
        log["trace_id2"] = TraceCtx.get_id()
        return log, ["trace_id2"]

    format_str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
        '<level>{level: <8}</level> | '
        '<level>{trace_id2}</level> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
        '<level>{message}</level>'
    )

    logger = LoggerInitializer(ObServe(ObserveConfig(
        observe_host='172.20.0.2',
        observe_port=40000,
        observe_base_dir="/logs",
        observe_username='root@isigning.com',
        observe_password='axzx@2025',
        observe_organization="algo_handwriting_database",  # 项目名
        observe_stream="dev")  # 版本等
    )).init_log(format_str=format_str, filter_func=my_filter)

    logger.info("LoggerInitializer-----format_str---my_filter---")

if __name__ == '__main__':
    import asyncio

    # asyncio.run(run_all_tests())
    asyncio.run(run_FastApi_test())
