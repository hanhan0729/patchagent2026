from enum import Enum


class Sanitizer(str, Enum):
    AddressSanitizer = "AddressSanitizer"
    UndefinedBehaviorSanitizer = "UndefinedBehaviorSanitizer"
    ThreadSanitizer = "ThreadSanitizer"
    KernelAddressSanitizer = "KernelAddressSanitizer"
    KernelConcurrencySanitizer = "KernelConcurrencySanitizer"
    BearSanitizer = "BearSanitizer"
    JazzerSanitizer = "JazzerSanitizer"