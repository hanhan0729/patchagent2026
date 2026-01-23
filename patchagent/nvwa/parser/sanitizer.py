from enum import StrEnum


class Sanitizer(StrEnum):
    AddressSanitizer = "AddressSanitizer"
    UndefinedBehaviorSanitizer = "UndefinedBehaviorSanitizer"
    ThreadSanitizer = "ThreadSanitizer"
    KernelAddressSanitizer = "KernelAddressSanitizer"
    KernelConcurrencySanitizer = "KernelConcurrencySanitizer"
    BearSanitizer = "BearSanitizer"
    JazzerSanitizer = "JazzerSanitizer"
