from email import header
import re
import os
from typing import Dict, Self, Tuple, Union, List, Any

from nvwa.parser.base import SanitizerReport
from nvwa.parser.cwe import CWE
from nvwa.logger import log
from nvwa.parser.sanitizer import Sanitizer
'''
#17117  REDUCE cov: 160 ft: 286 corp: 27/670b lim: 104 exec/s: 2445 rss: 1550Mb L: 25/98 MS: 4 CrossOver-Custom-EraseBytes-Custom-

== Java Exception: com.code_intelligence  .jazzer.api.FuzzerSecurityIssueHigh: Remote Code Execution
Unrestricted class/object creation based on externally controlled data may allow
remote code execution depending on available classes on the classpath.
        at jaz.Zer.reportFinding(Zer.java:114)
        at jaz.Zer.reportFindingIfEnabled(Zer.java:109)
        at jaz.Zer.readObject(Zer.java:384)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:568)
        at java.base/java.io.ObjectStreamClass.invokeReadObject(ObjectStreamClass.java:1100)
        at java.base/java.io.ObjectInputStream.readSerialData(ObjectInputStream.java:2423)
        at java.base/java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2257)
        at java.base/java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1733)
        at java.base/java.io.ObjectInputStream.readObject(ObjectInputStream.java:509)
        at java.base/java.io.ObjectInputStream.readObject(ObjectInputStream.java:467)
        at hudson.remoting.Capability.read(Capability.java:125)
        at hudson.remoting.ChannelBuilder.negotiate(ChannelBuilder.java:355)
        at hudson.remoting.ChannelBuilder.build(ChannelBuilder.java:282)
        at hudson.cli.CliProtocol$Handler.runCli(CliProtocol.java:77)
        at hudson.cli.CliProtocol$Handler.run(CliProtocol.java:64)
        at hudson.cli.CliProtocol.handle(CliProtocol.java:40)
        at fuzz.Main.fuzzerTestOneInput(Main.java:46)
DEDUP_TOKEN: d80c40dfa4f4d7d9
== libFuzzer crashing input ==
MS: 6 CopyPart-Custom-ChangeBit-Custom-CMP-Custom- DE: "\254\355\000\005sr\000\007jaz.Zer\000\000\000\000\000\000\000*\002\000\001B\000\011sanitizerxp\001"-; base unit: 13410c697f3f2164d5e149c87f6a90943948d6c9
0xac,0xed,0x0,0x5,0x73,0x72,0x0,0x7,0x6a,0x61,0x7a,0x2e,0x5a,0x65,0x72,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x2a,0x2,0x0,0x1,0x42,0x0,0x9,0x73,0x61,0x6e,0x69,0x74,0x69,0x7a,0x65,0x72,0x78,0x70,0x1,0xac,0xed,0x4,0x5,0x7a,0x0,0x0,0x0,0x0,0x0,0x0,0x5,0x0,0x0,0x0,0x5,0x0,
\254\355\000\005sr\000\007jaz.Zer\000\000\000\000\000\000\000*\002\000\001B\000\011sanitizerxp\001\254\355\004\005z\000\000\000\000\000\000\005\000\000\000\005\000
artifact_prefix='./'; Test unit written to ./crash-35679be30ec87e3f7ee668535b0ab53ef19e8f14
Base64: rO0ABXNyAAdqYXouWmVyAAAAAAAAACoCAAFCAAlzYW5pdGl6ZXJ4cAGs7QQFegAAAAAAAAUAAAAFAA==
reproducer_path='.'; Java reproducer written to ./Crash_35679be30ec87e3f7ee668535b0ab53ef19e8f14.java
'''

ldap_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueCritical: (LDAP Injection.*)")
jndi_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueCritical: (Remote JNDI Lookup.*)")
command_injection_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueCritical: (OS Command Injection.*)")
reflect_call_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueHigh: (load arbitrary library.*)")
regex_injection_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueLow: (Regular Expression Injection.*)")
ssti_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueCritical: (Script Engine Injection.*)")
ssrf_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueMedium: (Server Side Request Forgery.*)")
sqli_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueHigh: (SQL Injection.*)")
xpathi_header = re.compile(r"== Java Exception: com\.code_intelligence\.jazzer\.api\.FuzzerSecurityIssueHigh: (XPath Injection.*)")

class JazzerReport(SanitizerReport):
    def __init__(
        self,
        content: str,
        cwe: CWE,
        stacktrace: List[Tuple[str, str]],
        additional_info: Dict[str, Any] = {},
    ):
        super().__init__(Sanitizer.JazzerSanitizer, content, cwe, stacktrace, additional_info)

    @staticmethod
    def parse(content: str) -> Union[None, "SanitizerReport"]:
        def parse_header(lines: List[str], additional_info: Dict[str, Any]) -> CWE:
            header = ""
            while (line := lines.pop(0)) != "" and "== Java Exception: " not in line:
                pass
            while (line := lines.pop(0)) != "" and not line.startswith("\tat"):
                header += line + "\n"
            lines = [line] + lines

            if m := ldap_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.LDAP_INJECTION
            if m := jndi_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.REMOTE_JNDI_LOOKUP
            if m := command_injection_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.OS_COMMAND_INJECTION
            if m := reflect_call_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.LOAD_ARBITRARY_LIBRARY
            if m := regex_injection_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.REGULAR_EXPRESSION_INJECTION
            if m := ssti_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.SCRIPT_ENGINE_INJECTION
            if m := ssrf_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.SERVER_SIDE_REQUEST_FORGERY
            if m := sqli_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.SQL_INJECTION
            if m := xpathi_header.match(header):
                additional_info["issue"] = m.group(1)
                return CWE.XPATH_INJECTION
            return CWE.UNKNOWN
        
        def parse_stack(lines: List[str]) -> List[Tuple[str, str]]:
            stack = []
            while (line := lines.pop(0)) != "" and line.startswith("\tat"):
                classpath = line.split("(")[0].split("at ")[1].split(".")
                line_number = line.split(":")[-1].strip().strip(")")
                filename = line.split(":")[0].split("(")[1]
                function_name = classpath[-1]
                filename = "/".join(classpath[:-1]) + "/" + filename
                stack.append((filename, function_name + ":" + line_number))
            return stack
        try:
            lines = content.split("\n")
            if not lines:
                return None
            additional_info = {}
            cwe = parse_header(lines, additional_info)
            stacktrace = parse_stack(lines)
            return JazzerReport(content, cwe, stacktrace, additional_info)
        except Exception as e:
            log.error(f"Failed to parse Jazzer report: {e}")
            return None
    @property
    def summary(self) -> str:
        return "Jazzer report"
    
    def get_all_stacktrace(self) -> List[List[Tuple[str, str]]]:
        return [self.stacktrace] + [v for k, v in self.additional_info.items() if "stack" in k]


        