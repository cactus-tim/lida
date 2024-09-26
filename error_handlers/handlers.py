import asyncio
from functools import wraps
import time
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from error_handlers.errors import *
from bot_instance import logger
from bot_instance import bot

from handlers.error import safe_send_message


def db_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Error404 as e:
            logger.exception(str(e))
            return None
        except DatabaseConnectionError as e:
            logger.exception(str(e))
            return None
        except Error409 as e:
            logger.exception(str(e))
            return None
        except CompanyNameError as e:
            logger.exception(str(e))
            return None
        except FilterError as e:
            logger.exception(f"{str(e.message)}, for {str(e.id)}")
            await safe_send_message(bot, e.id, "К сожалению, мы не смогли найти подходяшую под ваши запрсы компанию")
            return None
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {str(e)}")
            return None
    return wrapper


# TODO: think about processing this errors
def gpt_error_handler(func):
    @wraps(func)
    async def wrapper(*args, retry_attempts=3, delay_between_retries=5, **kwargs):
        for attempt in range(retry_attempts):
            try:
                return await func(*args, **kwargs)
            except ParseError as e:
                logger.exception(f"{str(e)}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(delay_between_retries)
                else:
                    logger.exception(f"{str(e)}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except ContentError as e:
                logger.exception(f"{str(e)}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(delay_between_retries)
                else:
                    logger.exception(f"{str(e)}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except AuthenticationError as e:
                logger.exception(f"Authentication Error: {e}")
                return None
            except RateLimitError as e:
                logger.exception(f"Rate Limit Exceeded: {e}")
                return None
            except APIConnectionError as e:
                logger.exception(f"API Connection Error: {e}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(delay_between_retries)
                else:
                    logger.exception(f"API Connection Error: {e}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except APIError as e:
                logger.exception(f"API Error: {e}")
                return None
            except Exception as e:
                logger.exception(f"Неизвестная ошибка: {str(e)}")
                return None
    return wrapper


def parser_error_handler(func):
    @wraps(func)
    async def wrapper(*args, retry_attempts=3, delay_between_retries=5, **kwargs):
        for attempt in range(retry_attempts):
            try:
                return func(*args, **kwargs)
            except ParseError as e:
                logger.exception(f"{str(e)}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    time.sleep(delay_between_retries)
                else:
                    logger.exception(f"{str(e)}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except Exception as e:
                logger.exception(f"Неизвестная ошибка: {str(e)}")
                return None
    return wrapper


def mail_error_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP ошибка: {e}")
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP ошибка: {e}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
        finally:
            if 'mail' in kwargs and isinstance(kwargs['mail'], imaplib.IMAP4_SSL):
                try:
                    kwargs['mail'].logout()
                except Exception:
                    pass

    return wrapper
