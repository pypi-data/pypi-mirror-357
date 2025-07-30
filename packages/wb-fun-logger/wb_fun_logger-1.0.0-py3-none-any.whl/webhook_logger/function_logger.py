import time
import asyncio
import functools
import traceback

from loguru import logger
from dotenv import load_dotenv

from webhook_logger.config import CONFIG
from webhook_logger.utils.create_webhook_data import WebhookMessager

load_dotenv()

log_path = CONFIG.get(
    "log_file_path",
    env_var="LOG_FILE_PATH"
)

logger.configure(
    handlers=[
        {
            "sink": log_path,
            "rotation": "1 day",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{level}</level> - [{extra}] - <level>{message}</level>",
            "enqueue": True,
            "backtrace": True,
        }
    ]
)

def function_logger(sid, user_name=None, error_level=3):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger_context = logger.bind(sid=sid)
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger_context.info(
                    f"函数 {func.__qualname__} 执行成功 | 参数: {args}, {kwargs} | 耗时: {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_msg = f"函数 {func.__qualname__} 执行失败 | 参数: {args}, {kwargs} | 耗时: {duration:.3f}s | 错误: {str(e)}"
                logger_context.exception(error_msg)
                logger_context.error(f"错误 traceback: {traceback.format_exc()}")
                
                # 发送飞书通知
                try:
                    webhook_messager = WebhookMessager(message_target="feishu", machine_name=CONFIG.get("machine_id", env_var="MACHINE_ID"))
                    webhook_messager.post_data(msg=error_msg, user_id=user_name, is_error=True, error_level=error_level)
                except Exception as feishu_error:
                    logger_context.error(f"发送飞书通知失败: {str(feishu_error)}")
                
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger_context = logger.bind(sid=sid)
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger_context.info(
                    f"函数 {func.__qualname__} 执行成功 | 参数: {args}, {kwargs} | 耗时: {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_msg = f"函数 {func.__qualname__} 执行失败 | 参数: {args}, {kwargs} | 耗时: {duration:.3f}s | 错误: {str(e)}"
                logger_context.exception(error_msg)
                logger_context.error(f"错误 traceback: {traceback.format_exc()}")
                
                # 发送飞书通知
                try:
                    webhook_messager = WebhookMessager(message_target="feishu", machine_name=CONFIG.get("machine_id", env_var="MACHINE_ID"))
                    webhook_messager.post_data(msg=error_msg, user_id=user_name, is_error=True, error_level=error_level)
                except Exception as feishu_error:
                    logger_context.error(f"发送飞书通知失败: {str(feishu_error)}")
                
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
