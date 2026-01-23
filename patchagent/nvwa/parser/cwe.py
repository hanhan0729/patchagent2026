from enum import IntEnum


class CWE(IntEnum):
    UNKNOWN = 0
    CWE_787 = 1 << 0  # Out-of-bounds Write
    CWE_79 = 1 << 1  # Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
    CWE_89 = 1 << 2  # Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
    CWE_416 = 1 << 3  # Use After Free
    CWE_78 = 1 << 4  # Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
    CWE_20 = 1 << 5  # Improper Input Validation
    CWE_125 = 1 << 6  # Out-of-bounds Read
    CWE_22 = 1 << 7  # Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
    CWE_352 = 1 << 8  # Cross-Site Request Forgery (CSRF)
    CWE_434 = 1 << 9  # Unrestricted Upload of File with Dangerous Type
    CWE_862 = 1 << 10  # Missing Authorization
    CWE_476 = 1 << 11  # NULL Pointer Dereference
    CWE_287 = 1 << 12  # Improper Authentication
    CWE_190 = 1 << 13  # Integer Overflow or Wraparound
    CWE_502 = 1 << 14  # Deserialization of Untrusted Data
    CWE_77 = 1 << 15  # Improper Neutralization of Special Elements used in a Command ('Command Injection')
    CWE_119 = 1 << 16  # Improper Restriction of Operations within the Bounds of a Memory Buffer
    CWE_798 = 1 << 17  # Use of Hard-coded Credentials
    CWE_918 = 1 << 18  # Server-Side Request Forgery (SSRF)
    CWE_306 = 1 << 19  # Missing Authentication for Critical Function
    CWE_362 = 1 << 20  # Concurrent Execution using Shared Resource with Improper Synchronization ('
    CWE_269 = 1 << 21  # Improper Privilege Management
    CWE_94 = 1 << 22  # Improper Control of Generation of Code ('Code Injection')
    CWE_863 = 1 << 23  # Incorrect Authorization
    CWE_276 = 1 << 24  # Incorrect Default Permissions
    CWE_369 = 1 << 25  # Divide By Zero

    # for Asan
    NULL_POINTER_DEREFERENCE = CWE_476
    OUT_OF_BOUNDS = CWE_787 | CWE_125 | CWE_119
    USE_AFTER_FREE = CWE_416
    INTERGER_OVERFLOW = CWE_190
    DIVISION_BY_ZERO = CWE_369
    RACE_CONDITION = CWE_362
   
    # for Jazzer
    LDAP_INJECTION = CWE_20
    REMOTE_JNDI_LOOKUP = CWE_20
    OS_COMMAND_INJECTION = CWE_78 | CWE_20
    LOAD_ARBITRARY_LIBRARY = CWE_94 | CWE_20
    REGULAR_EXPRESSION_INJECTION = UNKNOWN 
    SCRIPT_ENGINE_INJECTION = CWE_94 | CWE_20 
    SERVER_SIDE_REQUEST_FORGERY = CWE_918 | CWE_20
    SQL_INJECTION = CWE_89 | CWE_20
    XPATH_INJECTION = CWE_89 | CWE_20
    
    ## TODO: Combine more CWEs


cwe_map = {
    CWE.NULL_POINTER_DEREFERENCE: "NULL Pointer Dereference",
    CWE.OUT_OF_BOUNDS: "Out of bounds",
    CWE.USE_AFTER_FREE: "Use After Free",
    CWE.INTERGER_OVERFLOW: "Integer Overflow",
    CWE.RACE_CONDITION: "Race Condition",
}

def cwe2str(cwe: CWE) -> str:
    return cwe_map.get(cwe, "Unknown CWE")
