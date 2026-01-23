from typing import Any, Dict, List, Tuple, Union

from nvwa.parser.cwe import CWE
from nvwa.parser.sanitizer import Sanitizer


class SanitizerReport:
    def __init__(
        self,
        sanitizer: Sanitizer,
        content: str,
        cwe: CWE,
        stacktrace: List[Tuple[str, str]],
        additional_info: Dict[str, Any] = {},
    ):

        self.sanitizer: Sanitizer = sanitizer
        self.content: str = content
        self.cwe: CWE = cwe
        self.stacktrace: List[Tuple[str, str]] = stacktrace
        self.additional_info: Dict[str, Any] = additional_info

    def __getitem__(self, key: str) -> Any:
        return self.additional_info[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_info[key] = value
        
    def get_all_stacktrace(self) -> List[List[Tuple[str, str]]]:
        return [self.stacktrace]

    @property
    def summary(self) -> str:
        return self.content

    @staticmethod
    def parse(content: str) -> Union[None, "SanitizerReport"]:
        return None
