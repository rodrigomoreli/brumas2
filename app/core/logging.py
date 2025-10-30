# app/core/logging.py

"""
Configuração de logging estruturado da aplicação.
Utiliza JSON para facilitar parsing e análise de logs em produção.
"""
import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger
from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Formatter customizado para adicionar campos extras aos logs.
    """

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # Adicionar campos customizados
        log_record["app"] = settings.PROJECT_NAME
        log_record["environment"] = getattr(settings, "ENVIRONMENT", "development")
        log_record["level"] = record.levelname
        log_record["logger_name"] = record.name

        # Adicionar informações de contexto se disponíveis
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_record["ip_address"] = record.ip_address


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configura o sistema de logging da aplicação.

    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger configurado
    """
    # Criar logger raiz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remover handlers existentes
    logger.handlers = []

    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Formatter JSON
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s", timestamp=True
    )
    console_handler.setFormatter(formatter)

    # Adicionar handler ao logger
    logger.addHandler(console_handler)

    # Configurar loggers de bibliotecas externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logger


# Criar logger global
logger = setup_logging(log_level=getattr(settings, "LOG_LEVEL", "INFO"))


def log_info(message: str, **kwargs):
    """Helper para log de informação com contexto."""
    logger.info(message, extra=kwargs)


def log_warning(message: str, **kwargs):
    """Helper para log de aviso com contexto."""
    logger.warning(message, extra=kwargs)


def log_error(message: str, **kwargs):
    """Helper para log de erro com contexto."""
    logger.error(message, extra=kwargs)


def log_debug(message: str, **kwargs):
    """Helper para log de debug com contexto."""
    logger.debug(message, extra=kwargs)


def log_critical(message: str, **kwargs):
    """Helper para log crítico com contexto."""
    logger.critical(message, extra=kwargs)
