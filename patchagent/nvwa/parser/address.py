import re
import os
from typing import Dict, Tuple, Union, List, Any

from nvwa.parser.base import SanitizerReport
from nvwa.parser.cwe import CWE
from nvwa.parser.sanitizer import Sanitizer


fpe_header = re.compile(r"==\d+==ERROR: AddressSanitizer: FPE on unknown address (.+)")
double_free_header = re.compile(r"==\d+==ERROR: AddressSanitizer: attempting double-free on (.+)")
invalid_free_header = re.compile(r"==\d+==ERROR: AddressSanitizer: attempting free on address which was not malloc\(\)-ed: (0x[\da-fA-F]+) in thread (T\d+)")
segv_header = re.compile(r"==\d+==ERROR: AddressSanitizer: SEGV on unknown address (.+)")
segv_header_alias = re.compile(r"==\d+==ERROR: AddressSanitizer: SEGV on unknown address (0x[\da-fA-F]+) (.+)")
common_header = re.compile(r"==\d+==ERROR: AddressSanitizer: ([\-_a-zA-Z]+)(.+)")

hint_pattern = re.compile(r"==\d+==Hint: (.+)")
location_pattern = re.compile(r"(WRITE|READ) of size (\d+) at ([\w\d]+) thread (.+)")
segv_access_pattern = re.compile(r"==\d+==The signal is caused by a (READ|WRITE) memory access\.")
stack_pattern = re.compile(r"^\s*#(\d+)\s+(0x[\w\d]+)\s+in\s+(.+?)\s+/root(.*)\s*")
memory_location_pattern = re.compile(r"^(0x[\da-f]+) is located (\d+) bytes (to the right of|to the left of|inside of|before|after) (\d+)-byte region \[(0x[\da-f]+),(0x[\da-f]+)\)")
stack_access_pattern = re.compile(r"Address (0x[\da-fA-F]+) is located in stack of thread (T\d+) at offset (\d+) in frame")
allocation_pattern = re.compile(r"^.*allocated by thread (.+) here:")
free_pattern = re.compile(r"^.*freed by thread (.+) here:")
summary_pattern = re.compile(r"^SUMMARY: (.+)")


class AddressSanitizerReport(SanitizerReport):
    ERROR_DESCRIPTIONS = {
        "heap-buffer-overflow": "the program tried to access a heap object outside of its allocated memory",
        "stack-buffer-overflow": "the program tried to access a stack object outside of its allocated memory",
        "stack-buffer-underflow": "the program tried to access a stack object outside of its allocated memory",
        "stack-use-after-return": "the program tried to access a stack object after the function that allocated it returned",
        "global-buffer-overflow": "the program tried to access a global object outside of its allocated memory",
        "heap-use-after-free": "the program tried to access a heap object after it was freed",
        "double-free": "the program tried to free a heap object that was already freed",
        "invalid-free": "the prograxm attempted to free a pointer that does not point to the start address of a heap object",
        "invalid-memory-access": "the program tried to access an invalid pointer",
        "negative-size-param": "the program passed a negative value as a size parameter",
        "memcpy-param-overlap": "the program passed overlapping source and destination pointers to memcpy",
        "stack-overflow": "the program's stack size exceeded the limit",
        "float-point-exception": "the program encountered a floating-point exception (eg. division by zero)",
    }

    ERROR_HINTS = (
        dict.fromkeys(
            ["heap-buffer-overflow", "stack-buffer-overflow", "stack-buffer-underflow", "global-buffer-overflow"],
            (
                "1. Find which variable indicates the size of the object and add bounds checking to prevent the overflow. \n"
                "2. Focused on some unsafe functions like memcpy, strcpy, strcat, strcmp, and so on, replace them with safer alternatives. \n"
                "3. If the overflow is unavoidable, consider allocating a larger buffer at allocation site. \n"
                "4. The error may caused by a integer overflow, consider all suspicious integer operations."
            ),
        )
        | dict.fromkeys(
            ["heap-use-after-free", "double-free", "invalid-free"],
            ("1. Ensure that the object is not accessed after it is freed. \n" "2. If the object is accessed after it is freed, consider swapping the order of the free and access operations. \n"),
        )
        | dict.fromkeys(
            ["invalid-memory-access"], ("1. Ensure that the pointer is valid before dereferencing it. \n" "2. If the pointer is not valid, consider checking the pointer before dereferencing it.")
        )
        | dict.fromkeys(
            ["negative-size-param"], ("1. Ensure that the size parameter is not negative. \n" "2. If the size parameter is negative, consider checking the size parameter before using it.")
        )
        | dict.fromkeys(
            ["memcpy-param-overlap"],
            ("1. Ensure that the source and destination pointers do not overlap. \n" "2. If the source and destination pointers overlap, consider using memmove instead of memcpy."),
        )
        | dict.fromkeys(
            ["float-point-exception"],
            (
                "1. If the operation is division(/), mod(%), you should consider the possibility of dividing by zero. \n"
                "2. If the operation is sqrt, log, pow, you should consider the possibility of taking the square root of a negative number."
            ),
        )
        | dict.fromkeys(
            ["stack-use-after-return"],
            (
                "1. Ensure that the object is not accessed after the function that allocated it returned. \n"
                "2. If the object is accessed after the function that allocated it returned, consider allocating the object on the heap instead of the stack."
            ),
        )
    )

    def __init__(
        self,
        content: str,
        cwe: CWE,
        stack_trace: List[Tuple[str, str]],
        additional_info: Dict[str, Any] = {},
    ):
        super().__init__(Sanitizer.AddressSanitizer, content, cwe, stack_trace, additional_info)

    @staticmethod
    def parse(content) -> Union[None, "AddressSanitizerReport"]:
        def parse_header(lines: List[str], additional_info: Dict[str, Any]) -> CWE:
            line = lines.pop(0)
            if double_free_header.match(line):
                additional_info["name"] = "double-free"
                return CWE.USE_AFTER_FREE

            if invalid_free_header.match(line):
                additional_info["name"] = "invalid-free"
                return CWE.USE_AFTER_FREE

            if segv_header.match(line):
                if (m := segv_header_alias.match(line)) is not None:
                    additional_info["address"] = m.group(1)
                additional_info["name"] = "invalid-memory-access"
                address = int(additional_info.get("address", "0x1000"), 16)
                if address < 0x1000:
                    return CWE.NULL_POINTER_DEREFERENCE
                else:
                    return CWE.OUT_OF_BOUNDS

            if fpe_header.match(line):
                additional_info["name"] = "float-point-exception"
                return CWE.DIVISION_BY_ZERO

            m = common_header.match(line)
            assert m is not None
            name, _ = m.groups()
            additional_info["name"] = name
            if name in ["heap-use-after-free", "stack-use-after-return"]:
                return CWE.USE_AFTER_FREE
            else:
                assert name in [
                    "heap-buffer-overflow",
                    "stack-buffer-overflow",
                    "stack-buffer-underflow",
                    "global-buffer-overflow",
                    "stack-overflow",
                    "negative-size-param",
                    "memcpy-param-overlap",
                ]
                return CWE.OUT_OF_BOUNDS

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

        def parse_heap_spatial_error(lines: List[str], additional_info: Dict[str, Any], access: bool = True) -> None:
            if access:
                m = location_pattern.match(lines.pop(0))
                assert m is not None
                location = m.groups()
                additional_info["length"] = int(location[1])
            error_stack = parse_stack(lines)

            line = lines.pop(0)
            alloc_stack = []
            if memory_location_pattern.match(line):
                m = memory_location_pattern.match(line)
                assert m is not None
                allocation = m.groups()

                if access:
                    additional_info["size"] = int(allocation[3])

                if free_pattern.match(lines[0]):
                    assert free_pattern.match(lines.pop(0))
                    parse_stack(lines)

                assert allocation_pattern.match(lines.pop(0))
                alloc_stack = parse_stack(lines)

                if access:
                    additional_info["offset"] = int(location[2], 16) - int(allocation[4], 16)
                    assert additional_info["offset"] < 0 or additional_info["offset"] + additional_info["length"] >= additional_info["size"]
            else:
                additional_info.pop("length", None)

            additional_info["error stack"] = error_stack
            additional_info["alloc stack"] = alloc_stack

        def parse_heap_temporal_error(lines: List[str], additional_info: Dict[str, Any], access: bool = True) -> None:
            assert not access or location_pattern.match(lines.pop(0))
            error_stack = parse_stack(lines)

            assert memory_location_pattern.match(lines.pop(0))
            assert free_pattern.match(lines.pop(0))
            free_stack = parse_stack(lines)

            assert allocation_pattern.match(lines.pop(0))
            alloc_stack = parse_stack(lines)

            additional_info["error stack"] = error_stack
            additional_info["alloc stack"] = alloc_stack
            additional_info["free stack"] = free_stack

        def parse_invalid_free_error(lines: List[str], additional_info: Dict[str, Any]) -> None:
            additional_info["error stack"] = parse_stack(lines)
            assert memory_location_pattern.match(lines.pop(0))
            additional_info["alloc stack"] = parse_stack(lines)

        def parse_stack_spatial_error(lines: List[str], additional_info: Dict[str, Any]) -> None:
            assert location_pattern.match(lines.pop(0))
            additional_info["error stack"] = parse_stack(lines)
            assert stack_access_pattern.match(lines.pop(0))
            additional_info["frame"] = parse_stack(lines)[0]

        def parse_global_spatial_error(lines: List[str], additional_info: Dict[str, Any]) -> None:
            assert location_pattern.match(lines.pop(0))
            additional_info["error stack"] = parse_stack(lines)

        def parse_invalid_memory_access(lines: List[str], additional_info: Dict[str, Any]) -> None:
            assert segv_access_pattern.match(lines.pop(0))
            additional_info["error stack"] = parse_stack(lines)

        def parse_other_error(lines: List[str], additional_info: Dict[str, Any]) -> None:
            while lines[0].strip()[0] != "#":
                lines.pop(0)
            additional_info["error stack"] = parse_stack(lines)

        if (m := re.search(r"==[0-9]+==ERROR: AddressSanitizer: .*SUMMARY: AddressSanitizer", content, re.DOTALL)) is not None:
            content = m.group(0)
        else:
            additional_info = {}
            lines = [l.strip() for l in content.splitlines() if not hint_pattern.match(l)]
            parse_other_error(lines, additional_info)
            if "error stack" not in additional_info:
                return None

            additional_info["name"] = "unknown"
            return AddressSanitizerReport(content, CWE.UNKNOWN, additional_info["error stack"], additional_info)

        lines = [l.strip() for l in content.splitlines() if not hint_pattern.match(l)]
        additional_info = {}

        try:
            cwe = parse_header(lines, additional_info)
            if additional_info["name"] == "heap-buffer-overflow":
                parse_heap_spatial_error(lines, additional_info, access=True)
            elif additional_info["name"] in ["memcpy-param-overlap"]:
                parse_heap_spatial_error(lines, additional_info, access=False)
            elif additional_info["name"] == "negative-size-param":
                additional_info["error stack"] = parse_stack(lines)
            elif additional_info["name"] in "heap-use-after-free":
                parse_heap_temporal_error(lines, additional_info, access=True)
            elif additional_info["name"] == "double-free":
                parse_heap_temporal_error(lines, additional_info, access=False)
            elif additional_info["name"] == "invalid-free":
                parse_invalid_free_error(lines, additional_info)
            elif additional_info["name"] in ["stack-buffer-overflow", "stack-buffer-underflow", "stack-use-after-return"]:
                parse_stack_spatial_error(lines, additional_info)
            elif additional_info["name"] == "global-buffer-overflow":
                parse_global_spatial_error(lines, additional_info)
            elif additional_info["name"] == "invalid-memory-access":
                parse_invalid_memory_access(lines, additional_info)
            else:
                parse_other_error(lines, additional_info)

            stacktrace = additional_info.pop("error stack")
            return AddressSanitizerReport(content, cwe, stacktrace, additional_info)
        except (AssertionError, IndexError):
            return None

    @property
    def summary(self) -> str:
        def summarize_stack(stack):
            s = ""
            for function, source in stack[:-1]:
                s += f"at {source} within {function} which is called \n"
            s += f"at {stack[-1][1]} within {stack[-1][0]}."
            return s

        if self["name"] == "unknown":
            summary = "The sanitizer detected an error. Here is the stacktrace: \n"
            summary += summarize_stack(self.stacktrace)
            return summary

        error_type = self["name"]
        summary = f"The sanitizer detected a {error_type} error. It means that {self.ERROR_DESCRIPTIONS[error_type]}. "

        if "size" in self.additional_info and "length" in self.additional_info and "offset" in self.additional_info:
            size, length, offset = self.additional_info["size"], self.additional_info["length"], self.additional_info["offset"]
            summary += f"The size of the object is {size} bytes, but the program tried to access {length} bytes at offset {offset}. "
        if "address" in self.additional_info:
            summary += f"The address is {self.additional_info.get('address')}. "

        summary += "\n\nThe error happened "
        summary += summarize_stack(self.stacktrace)

        if stack := self.additional_info.get("alloc stack", []):
            summary += "\n\nThe object was allocated "
            summary += summarize_stack(stack)

        if stack := self.additional_info.get("free stack", []):
            summary += "\n\nThe object was freed "
            summary += summarize_stack(stack)

        if "frame" in self.additional_info:
            summary += "\n\nThe object is defined "
            summary += summarize_stack([self.additional_info.get("frame")])

        if error_type in self.ERROR_HINTS:
            summary += f"\n\nTo patch the error, you could consider the following options: \n{self.ERROR_HINTS[error_type]}"

        return summary

    def get_all_stacktrace(self) -> List[List[Tuple[str, str]]]:
        return [self.stacktrace] + [v for k, v in self.additional_info.items() if "stack" in k]
