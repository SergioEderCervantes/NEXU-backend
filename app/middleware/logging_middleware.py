import time
import logging
logger = logging.getLogger("app")

def log_request_time(app):
    @app.before_request
    def start_timer():
        from flask import g, request
        g.start_time = time.perf_counter()
        logger.info(f"→ {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        from flask import g, request
        if hasattr(g, 'start_time'):
            duration = time.perf_counter() - g.start_time
            logger.info(f"← {request.method} {request.path} [{response.status_code}] {duration:.3f}s")
        return response
