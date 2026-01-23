from typing import Union

from nvwa.sky.task import PatchTask

from nvwa.lsp.clangd import ClangdServer
from nvwa.lsp.ctags import CtagsServer
from nvwa.lsp.language import LanguageType, LanguageServer

SERVER_POOL: list[tuple[type[LanguageServer], dict]] = [
    (ClangdServer, {}),
    (CtagsServer, {})
]

def get_language(task: PatchTask) -> str:
    return LanguageType.C

def find_backend(task: PatchTask, interface: str)  -> Union[None, LanguageServer]:
    key = f"{task.project}-{task.tag}"
    language = get_language(task)
    for server, pool in SERVER_POOL:
        if language in server.supported_languages() and hasattr(server, interface):
            if key not in pool:
                pool[key] = server(task)
            return pool[key]
