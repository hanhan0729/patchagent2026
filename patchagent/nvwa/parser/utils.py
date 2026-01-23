from typing import Union
from nvwa.parser.base import SanitizerReport
from nvwa.parser.jazzer import JazzerReport
from nvwa.parser.address import AddressSanitizerReport
from nvwa.parser.undefined import UndefinedBehaviorSanitizerReport
from nvwa.parser.kerneladdress import KernelAddressSanitizerReport
from nvwa.parser.sanitizer import Sanitizer


def parse(content: str, sanitizer: Sanitizer) -> Union[None, "SanitizerReport"]:
    __sanitizer_report_classes_map__ = {
        Sanitizer.AddressSanitizer: AddressSanitizerReport,
        Sanitizer.UndefinedBehaviorSanitizer: UndefinedBehaviorSanitizerReport,
        Sanitizer.JazzerSanitizer: JazzerReport,
        Sanitizer.KernelAddressSanitizer: KernelAddressSanitizerReport,
    }
    if sanitizer in __sanitizer_report_classes_map__:
        return __sanitizer_report_classes_map__[sanitizer].parse(content)
    return None
