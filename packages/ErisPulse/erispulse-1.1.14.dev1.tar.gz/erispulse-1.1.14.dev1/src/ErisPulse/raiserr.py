"""
# 错误管理系统

提供错误类型注册、抛出和管理功能，集成全局异常处理。

## API 文档
### 错误注册：
    - register(name, doc="", base=Exception): 注册新的错误类型
    - info(name: str = None): 获取错误类型信息

### 错误抛出：
    - __getattr__(name): 动态获取错误抛出函数
    - ErrorType(msg, exit=False): 抛出注册的错误类型

### 全局处理：
    - global_exception_handler: 全局同步异常处理器
    - async_exception_handler: 全局异步异常处理器

### 示例用法：

```
from ErisPulse import sdk

# 注册自定义错误
sdk.raiserr.register("MyError", doc="自定义错误描述")

# 抛出错误
sdk.raiserr.MyError("发生了错误", exit=False)

# 获取错误信息
error_info = sdk.raiserr.info("MyError")
```

"""

import sys
import traceback
import asyncio

class Error:
    def __init__(self):
        self._types = {}

    def register(self, name, doc="", base=Exception):
        if name not in self._types:
            err_cls = type(name, (base,), {"__doc__": doc})
            self._types[name] = err_cls
        return self._types[name]

    def __getattr__(self, name):
        def raiser(msg, exit=False):
            from .logger import logger
            err_cls = self._types.get(name) or self.register(name)
            exc = err_cls(msg)

            red = '\033[91m'
            reset = '\033[0m'

            logger.error(f"{red}{name}: {msg} | {err_cls.__doc__}{reset}")
            logger.error(f"{red}{ ''.join(traceback.format_stack()) }{reset}")

            if exit:
                raise exc
        return raiser

    def info(self, name: str = None):
        result = {}
        for err_name, err_cls in self._types.items():
            result[err_name] = {
                "type": err_name,
                "doc": getattr(err_cls, "__doc__", ""),
                "class": err_cls,
            }
        if name is None:
            return result
        err_cls = self._types.get(name)
        if not err_cls:
            return None
        return {
            "type": name,
            "doc": getattr(err_cls, "__doc__", ""),
            "class": err_cls,
        }

raiserr = Error()

# 全局异常处理器
def global_exception_handler(exc_type, exc_value, exc_traceback):
    from .logger import logger
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"未处理的异常被捕获:\n{error_message}")
    raiserr.CaughtExternalError(
        f"检测到外部异常，请优先使用 sdk.raiserr 抛出错误。\n原始异常: {exc_type.__name__}: {exc_value}\nTraceback:\n{error_message}"
    )
sys.excepthook = global_exception_handler

def async_exception_handler(loop, context):
    from .logger import logger
    exception = context.get('exception')
    message = context.get('message', 'Async error')
    if exception:
        tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        logger.error(f"异步任务异常: {message}\n{tb}")
        raiserr.CaughtExternalError(
            f"检测到异步任务异常，请优先使用 sdk.raiserr 抛出错误。\n原始异常: {type(exception).__name__}: {exception}\nTraceback:\n{tb}"
        )
    else:
        logger.warning(f"异步任务警告: {message}")
asyncio.get_event_loop().set_exception_handler(async_exception_handler)