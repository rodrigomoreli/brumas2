# /app/middleware/logging.py

"""
Middleware para logging de requisições HTTP.
Registra todas as requisições e respostas com informações detalhadas.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra todas as requisições HTTP.
    Adiciona request_id único para rastreamento.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar ID único para a requisição
        request_id = str(uuid.uuid4())

        # Adicionar request_id ao state da requisição
        request.state.request_id = request_id

        # Capturar informações da requisição
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"

        # Log de início da requisição
        logger.info(
            f"Request started: {method} {url}",
            extra={
                "request_id": request_id,
                "method": method,
                "url": url,
                "ip_address": client_host,
                "user_agent": request.headers.get("user-agent", "unknown"),
            },
        )

        # Medir tempo de processamento
        start_time = time.time()

        try:
            # Processar requisição
            response = await call_next(request)

            # Calcular tempo de processamento
            process_time = time.time() - start_time

            # Log de conclusão da requisição
            logger.info(
                f"Request completed: {method} {url} - Status: {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "process_time": round(process_time, 3),
                    "ip_address": client_host,
                },
            )

            # Adicionar request_id ao header da resposta
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log de erro
            process_time = time.time() - start_time

            logger.error(
                f"Request failed: {method} {url} - Error: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time": round(process_time, 3),
                    "ip_address": client_host,
                },
                exc_info=True,
            )

            raise
