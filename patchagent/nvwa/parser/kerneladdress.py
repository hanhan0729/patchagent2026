import re
import os
from typing import Dict, Tuple, Union, List, Any


from nvwa.parser.base import SanitizerReport
from nvwa.parser.cwe import CWE
from nvwa.parser.sanitizer import Sanitizer


use_after_free_headr = re.compile(r"BUG: KASAN: use-after-free in (.+)")
null_ptr_deref_header = re.compile(r"BUG: KASAN: null-ptr-deref in (.+)")
slab_out_of_bounds_header = re.compile(r"BUG: KASAN: slab-out-of-bounds in (.+)")
common_header = re.compile(r"(BUG: )?KASAN: ([\-_a-zA-Z]+)(.+)")
location_pattern = re.compile(r"(Write|Read) of size (\d+) at addr ([\w\d]+) by task (.+)")
stack_pattern = re.compile(r"^\s*(\??\s*[\w_.]+)(?:\+0x[\da-fA-F]+/0x[\da-fA-F]+)?\s+([^:]+:\d+:\d+)(?: \[inline\])?\s*$")
allocation_pattern = re.compile(r"Allocated by task (.+)")
free_pattern = re.compile(r"Freed by task (.+)")
debug_function_list = ['__kmem_cache_alloc_lru','slab_alloc','slab_alloc_node','slab_post_alloc_hook','slab_free','slab_free_freelist_hook','slab_free_hook','__dump_stack','dump_stack_lvl','print_report','__virt_addr_valid','__phys_addr','kasan_report','trace_event_raw_event_sched_switch',
                       '__sanitizer_cov_trace_switch','entry_SYSCALL_64_after_hwframe','do_syscall_64','panic_print_sys_info.part.0','kasan_report.cold',
                       'trace_event_raw_event_sched_switch','panic',"end_report","end_report.part.0","check_panic_on_warn.cold","die_addr.cold","exc_general_protection",
                       "asm_exc_general_protection","syscall_enter_from_user_mode","lockdep_hardirqs_on","lockdep_hardirqs_on_prepare","kasan_check_range","end_report.cold","print_address_description"
                       ,"kasan_save_stack","get_current","kasan_set_track","kasan_save_track","poison_kmalloc_redzone","__kasan_kmalloc","poison_slab_object","__kasan_slab_free","show_stack","dump_backtrace"]


class KernelAddressSanitizerReport(SanitizerReport):
    ERROR_DESCRIPTIONS = {
        "out-of-bounds": "the kernel tried to access a kernel heap object outside of its allocated memory",
        "slab-out-of-bounds": "the kernel tried to access a kernel heap object outside of its allocated memory",
        "vmalloc-out-of-bounds": "the kernel tried to access an address outside of the vmalloc memory area",
        "use-after-free": "the kernel tried to access a kernel heap object after it was freed",
        "slab-use-after-free": "the kernel tried to access a kernel heap object after it was freed",
        "null-ptr-deref": "the kernel tried to dereference a null pointer",
        "wild-memory-access": "the kernel tried to access an invalid memory area",
        "user-memory-access": "the kernel tried to access an invalid user memory area",
        "stack-out-of-bounds": "the kernel tried to access a stack object outside of its allocated memory",
    }

    ERROR_HINTS = (
        dict.fromkeys(
            ["slab-out-of-bounds", "out-of-bounds", "vmalloc-out-of-bounds", "stack-out-of-bounds"],
            (
                "1. Find which variable indicates the size of the object and add bounds checking to prevent the overflow. \n"
                "2. Focused on some unsafe functions like memcpy, strcpy, strcat, strcmp, and so on, replace them with safer alternatives. \n"
                "3. If the overflow is unavoidable, consider allocating a larger buffer at allocation site. \n"
                "4. The error may caused by a integer overflow, consider all suspicious integer operations."
            ),
        )
        | dict.fromkeys(
            ["use-after-free", "slab-use-after-free"],
            ("1. Ensure that the object is not accessed after it is freed. \n" "2. If the object is accessed after it is freed, consider swapping the order of the free and access operations. \n"),
        )
        | dict.fromkeys(
            ["null-ptr-deref"], ("1. Ensure that the pointer is valid before dereferencing it. \n" "2. If the pointer is not valid, consider checking the pointer before dereferencing it.")
        )
        | dict.fromkeys(
            ["user-memory-access"], ("1. Ensure that the user memory is valid before accessing it. \n" "2. If the user memory is not valid, consider checking the user memory before accessing it.")
        )
    )

    def __init__(
        self,
        content: str,
        cwe: CWE,
        stack_trace: List[Tuple[str, str]],
        additional_info: Dict[str, Any] = {},
    ):
        super().__init__(Sanitizer.KernelAddressSanitizer, content, cwe, stack_trace, additional_info)

    @staticmethod
    def parse(content) -> Union[None, "KernelAddressSanitizerReport"]:
        def parse_header(lines: List[str], additional_info: Dict[str, Any]) -> CWE:
            line = lines.pop(0)

            m = common_header.match(line)
            assert m is not None
            assert len(m.groups()) == 3
            _, name, _ = m.groups()

            additional_info["name"] = name
            if name in ["slab-use-after-free", "use-after-free"]:
                return CWE.USE_AFTER_FREE

            if name in ["null-ptr-deref", "wild-memory-access", "user-memory-access"]:
                return CWE.NULL_POINTER_DEREFERENCE

            assert name in [
                "slab-out-of-bounds",
                "out-of-bounds",
                "vmalloc-out-of-bounds",
                "stack-out-of-bounds",
            ]
            return CWE.OUT_OF_BOUNDS

        def parse_stack(lines: List[str]) -> List[Tuple[str, str]]:
            stack = []
            while (line := lines.pop(0)):
                if m := stack_pattern.match(line):
                    function, source = m.groups()
                    path, line_no, col_no = source.split(":")
                    stack.append((function, f"{os.path.normpath(path)}:{line_no}:{col_no}"))
                else:
                    break
            return stack

        def parse_heap_spatial_error(lines: List[str], additional_info: Dict[str, Any]) -> None:
            while lines:
                line = lines.pop(0)
                if location_pattern.match(line):
                    break

            error_stack = parse_stack(lines)
            additional_info["error stack"] = error_stack
            while lines:
                line = lines.pop(0)
                if allocation_pattern.match(line):
                    alloc_stack = parse_stack(lines)
                    additional_info["alloc stack"] = alloc_stack
                    continue
                elif free_pattern.match(line):
                    free_stack = parse_stack(lines)
                    additional_info["free stack"] = free_stack
                    break 

        def parse_heap_temporal_error(lines: List[str], additional_info: Dict[str, Any]) -> None:
            while lines:
                line = lines.pop(0)
                if location_pattern.match(line):
                    break

            error_stack = parse_stack(lines)
            additional_info["error stack"] = error_stack
            while lines:
                line = lines.pop(0)
                if allocation_pattern.match(line):
                    alloc_stack = parse_stack(lines)
                    additional_info["alloc stack"] = alloc_stack
                    continue
                elif free_pattern.match(line):
                    free_stack = parse_stack(lines)
                    additional_info["free stack"] = free_stack
                    break 
            

        def parse_null_ptr_deref(lines: List[str], additional_info: Dict[str, Any]) -> None:
            while lines:
                line = lines.pop(0)
                if location_pattern.match(line):
                    break
            
            error_stack = parse_stack(lines)
            additional_info["error stack"] = error_stack

        if (m := re.search(r"(BUG: )?KASAN: ([\-_a-zA-Z]+)(.+)", content, re.DOTALL)) is not None:
            content = m.group(0)
        else:
            return None

        lines = content.splitlines()
        lines = [re.sub(r"^\[\s*.*?\](\[\s*.*?\])?\s*", "", line) for line in lines]  # remove timestamp
        lines = [line.strip() for line in lines if line.strip() != ""]  # remove empty lines
        forbidden_keywords = ["RIP", "Code", "RSP", "RAX", "RDX", "RBP", "R10", "R13", "</", "CORRUPTED:", "MAINTAINERS ","CPU: ","Hardware name:","Call Trace:","<IRQ>","<TASK>","audit:","Workqueue:"]
        lines = [
            line for line in lines if all(keyword not in line for keyword in forbidden_keywords)
        ]
        
        additional_info = {}
        try:
            cwe = parse_header(lines, additional_info)
            if additional_info["name"] in ["slab-out-of-bounds", "out-of-bounds", "vmalloc-out-of-bounds"]:
                parse_heap_spatial_error(lines, additional_info)
            elif additional_info["name"] in ["use-after-free", "slab-use-after-free"]:
                parse_heap_temporal_error(lines, additional_info)
            elif additional_info["name"] in ["null-ptr-deref", "stack-out-of-bounds", "wild-memory-access", "user-memory-access"]:
                parse_null_ptr_deref(lines, additional_info)

            stacktrace = additional_info.pop("error stack")
            return KernelAddressSanitizerReport(content, cwe, stacktrace, additional_info)
        except (AssertionError, IndexError):
            return None

    @property
    def summary(self) -> str:
        def summarize_stack(stack):
            s = ""
            for function, source in stack[:-1]:
                if "kasan" in function or "kasan" in source or function in debug_function_list or "__x64_sys" in function or "__do_sys_" in function or "__se_sys_" in function or "do_syscall_" in function or "entry_SYSCALL_64_" in function:
                    continue
                s += f"at {source} within {function} which is called \n"
            s += f"at {stack[-1][1]} within {stack[-1][0]}."
            return s

        error_type = self["name"]
        summary = f"The sanitizer detected a {error_type} error. It means that {self.ERROR_DESCRIPTIONS[error_type]}. "
        
        summary += "\n\nThe error happened "
        summary += summarize_stack(self.stacktrace)

        if stack := self.additional_info.get("alloc stack", []):
            if len(stack) > 1:
                summary += "\n\nThe object was allocated "
                summary += summarize_stack(stack)

        if stack := self.additional_info.get("free stack", []):
            if len(stack) > 1:
                summary += "\n\nThe object was freed "
                summary += summarize_stack(stack)

        if error_type in self.ERROR_HINTS:
            summary += f"\n\nTo patch the error, you could consider the following options: \n{self.ERROR_HINTS[error_type]}"
        
        return summary

    def get_all_stacktrace(self) -> List[List[Tuple[str, str]]]:
        return [self.stacktrace] + [v for k, v in self.additional_info.items() if "stack" in k]
