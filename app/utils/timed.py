import time
import logging
logger = logging.getLogger('app')

def timed_task(task_name: str):
    def decorator(func):
        def wrapper(*args,**kwargs):
            start = time.perf_counter()
            logger.info(f"Inicio de tarea: {task_name}")
            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start
                logger.info(f"Tarea: {task_name} completada en: {duration:.2f}s")
                return result
            except Exception:
                duration = time.perf_counter() - start
                logger.exception(f"Error en tarea:  {task_name} tras: {duration:.2f}s")
                raise
        return wrapper
    return decorator
