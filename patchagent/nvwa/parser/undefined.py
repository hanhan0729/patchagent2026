import re
import os
from typing import Dict, Tuple, Union, List, Any

from nvwa.parser.base import SanitizerReport
from nvwa.parser.cwe import CWE
from nvwa.logger import log
from nvwa.parser.sanitizer import Sanitizer


stack_pattern = re.compile(r"^\s*#(\d+)\s+(0x[\w\d]+)\s+in\s+(.+?)\s+/root(.*)\s*")


class UndefinedBehaviorSanitizerReport(SanitizerReport):
    def __init__(
        self,
        content: str,
        cwe: CWE,
        stacktrace: List[Tuple[str, str]],
        additional_info: Dict[str, Any] = {},
    ):
        super().__init__(Sanitizer.UndefinedBehaviorSanitizer, content, cwe, stacktrace, additional_info)

    @property
    def summary(self) -> str:
        def summarize_stack(stack):
            s = ""
            for function, source in stack[:-1]:
                s += f"at {source} within {function} which is called \n"
            s += f"at {stack[-1][1]} within {stack[-1][0]}."
            return s

        return self.additional_info["description"] + "\n" + summarize_stack(self.stacktrace)

    @staticmethod
    def parse(content: str) -> Union[None, "SanitizerReport"]:
        def parse_stack(lines: List[str]) -> List[Tuple[str, str]]:
            stack, i = [], 0
            while (line := lines.pop(0)).strip().startswith("#"):
                if m := stack_pattern.match(line):
                    id, address, function, source = m.groups()
                    if len(result := source.split(":")) == 3:
                        path, line_no, column_no = result
                        stack.append((function, f"{os.path.normpath(path)}:{line_no}:{column_no}"))
                    else:
                        path, line_no = result
                        stack.append((function, f"{os.path.normpath(path)}:{line_no}"))

                    assert line == f"#{id} {address} in {function} /root{source}"
                    assert int(id) == i
                i += 1

            return stack

        if "UndefinedBehaviorSanitizer" not in content:
            return None

        cwe = CWE.INTERGER_OVERFLOW
        stacktrace = []
        additional_info = {}

        lines = [l.strip() for l in content.splitlines()]
        additional_info["description"] = lines.pop(0)
        stacktrace = parse_stack(lines)

        return UndefinedBehaviorSanitizerReport(content, cwe, stacktrace, additional_info)
