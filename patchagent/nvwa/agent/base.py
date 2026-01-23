import openai
import httpx
import traceback

from abc import ABC, abstractmethod
from nvwa.context import ContextManager
from nvwa.logger import log


class BaseAgent(ABC):
    def __init__(self, context_manager: ContextManager):
        self.context_manager: ContextManager = context_manager

    @abstractmethod
    def _apply(self):
        pass

    def apply(self):
        if self.context_manager.patch is not None:
            return
        log.info(f"Applying {self.__class__.__name__}")

        try:
            self._apply()
        except openai.APIError as e:
            log.error(f"OpenAI API error: {e}")
            log.error(traceback.format_exc())
        except httpx.RemoteProtocolError as e:
            log.error(f"HTTPX error: {e}")
            log.error(traceback.format_exc())
        except Exception as e:
            log.error(f"Unknown Error: {e}")
            log.error(traceback.format_exc())
