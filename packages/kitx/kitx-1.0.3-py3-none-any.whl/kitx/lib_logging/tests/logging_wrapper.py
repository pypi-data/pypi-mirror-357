from kitx.lib_logging import async_logging_decorator, LoggerInitializer, ObServe, ObserveConfig

logger = LoggerInitializer(ObServe(ObserveConfig(
    observe_host='172.20.0.2',
    observe_port=40000,
    observe_base_dir="/logs",
    observe_username='root@isigning.com',
    observe_password='axzx@2025',
    observe_organization="lib_xxx",  # 项目名
    observe_stream="dev"  # 环境+版本等
))).init_log()


# 使用示例
@async_logging_decorator(logger)
async def async_function(a, b):
    logger.info(f"执行异步函数，参数: {a}, {b}")
    await asyncio.sleep(1)
    return a + b


async def main():
    result = await async_function(3, 4)
    logger.info(f"结果: {result}")
    await asyncio.sleep(1)  # await async

if __name__ == '__main__':
    # 测试
    import asyncio

    asyncio.run(main())
