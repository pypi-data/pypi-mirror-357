"""
# 日志系统

提供模块化、多级别的日志记录功能，支持内存存储和文件输出。

## API 文档
### 基本操作：
    - debug(msg, *args, **kwargs):      调试信息
    - info(msg, *args, **kwargs):       运行信息  
    - warning(msg, *args, **kwargs):    警告信息
    - error(msg, *args, **kwargs):      错误信息
    - critical(msg, *args, **kwargs):   致命错误并终止程序

### 日志控制：
    - set_level(level):                     设置全局日志级别
    - set_module_level(module_name, level): 设置模块日志级别

### 日志存储：
    - save_logs(path):          保存内存中的日志到文件
    - set_output_file(path):    设置日志输出文件

### 示例用法：

```
from ErisPulse import sdk

# 基本日志记录
sdk.logger.debug("调试信息")
sdk.logger.info("运行状态")

# 模块级日志控制
sdk.logger.set_module_level("MyModule", "DEBUG")

# 异常捕获
@sdk.logger.catch
def risky_function():
    raise Exception("出错了")
```

## 准备弃用

catch(func_or_level=None, level="error"): 异常捕获装饰器
- 原因: 异常捕获功能已集成到 raiserr 模块中，建议使用 raiserr 进行异常处理。

"""

import logging
import inspect
import datetime
import functools

class Logger:
    def __init__(self):
        self._logs = {}
        self._module_levels = {}
        self._logger = logging.getLogger("ErisPulse")
        self._logger.setLevel(logging.DEBUG)
        self._file_handler = None
        if not self._logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(console_handler)

    def set_level(self, level: str):
        level = level.upper()
        if hasattr(logging, level):
            self._logger.setLevel(getattr(logging, level))

    def set_module_level(self, module_name: str, level: str) -> bool:
        from .db import env
        if not env.get_module_status(module_name):
            self._logger.warning(f"模块 {module_name} 未启用，无法设置日志等级。")
            return False
        level = level.upper()
        if hasattr(logging, level):
            self._module_levels[module_name] = getattr(logging, level)
            self._logger.info(f"模块 {module_name} 日志等级已设置为 {level}")
            return True
        else:
            self._logger.error(f"无效的日志等级: {level}")
            return False

    def set_output_file(self, path: str | list):
        if self._file_handler:
            self._logger.removeHandler(self._file_handler)
            self._file_handler.close()

        if isinstance(path, str):
            path = [path]

        for p in path:
            try:
                file_handler = logging.FileHandler(p, encoding='utf-8')
                file_handler.setFormatter(logging.Formatter("%(message)s"))
                self._logger.addHandler(file_handler)
                self._logger.info(f"日志输出已设置到文件: {p}")
            except Exception as e:
                self._logger.error(f"无法设置日志文件 {p}: {e}")
                raise e

    def save_logs(self, path: str | list):
        if self._logs == None:
            self._logger.warning("没有log记录可供保存。")
            return
        if isinstance(path, str):
            path = [path]

        for p in path:
            try:
                with open(p, "w", encoding="utf-8") as file:
                    for module, logs in self._logs.items():
                        file.write(f"Module: {module}\n")
                        for log in logs:
                            file.write(f"  {log}\n")
                    self._logger.info(f"日志已被保存到：{p}。")
            except Exception as e:
                self._logger.error(f"无法保存日志到 {p}: {e}。")
                raise e

    def catch(self, func_or_level=None, level="error"):
        if isinstance(func_or_level, str):
            return lambda func: self.catch(func, level=func_or_level)
        if func_or_level is None:
            return lambda func: self.catch(func, level=level)
        func = func_or_level

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                import traceback
                error_info = traceback.format_exc()

                module_name = func.__module__
                if module_name == "__main__":
                    module_name = "Main"
                func_name = func.__name__

                error_msg = f"Exception in {func_name}: {str(e)}\n{error_info}"

                log_method = getattr(self, level, self.error)
                log_method(error_msg)

                return None
        return wrapper

    def _save_in_memory(self, ModuleName, msg):
        if ModuleName not in self._logs:
            self._logs[ModuleName] = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{timestamp} - {msg}"
        self._logs[ModuleName].append(msg)

    def _get_effective_level(self, module_name):
        return self._module_levels.get(module_name, self._logger.level)

    def _get_caller(self):
        frame = inspect.currentframe().f_back.f_back
        module = inspect.getmodule(frame)
        module_name = module.__name__
        if module_name == "__main__":
            module_name = "Main"
        if module_name.endswith(".Core"):
            module_name = module_name[:-5]
        return module_name

    def debug(self, msg, *args, **kwargs):
        caller_module = self._get_caller()
        if self._get_effective_level(caller_module) <= logging.DEBUG:
            self._save_in_memory(caller_module, msg)
            self._logger.debug(f"[{caller_module}] {msg}", *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        caller_module = self._get_caller()
        if self._get_effective_level(caller_module) <= logging.INFO:
            self._save_in_memory(caller_module, msg)
            self._logger.info(f"[{caller_module}] {msg}", *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        caller_module = self._get_caller()
        if self._get_effective_level(caller_module) <= logging.WARNING:
            self._save_in_memory(caller_module, msg)
            self._logger.warning(f"[{caller_module}] {msg}", *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        caller_module = self._get_caller()
        if self._get_effective_level(caller_module) <= logging.ERROR:
            self._save_in_memory(caller_module, msg)
            self._logger.error(f"[{caller_module}] {msg}", *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        caller_module = self._get_caller()
        if self._get_effective_level(caller_module) <= logging.CRITICAL:
            self._save_in_memory(caller_module, msg)
            self._logger.critical(f"[{caller_module}] {msg}", *args, **kwargs)
            from .raiserr import raiserr
            raiserr.register("CriticalError", doc="发生致命错误")
            raiserr.CriticalError(f"程序发生致命错误：{msg}", exit=True)

logger = Logger()