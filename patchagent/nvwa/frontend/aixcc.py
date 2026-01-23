from nvwa.sky.task import PatchTask

class AIxCCTask:
    def __init__(self) -> None:
        self.count = 0
        self.running = False

    def run(self) -> None:
        pass

    @property
    def tag(self) -> str:
        return 'default'
    
    @staticmethod
    def parse(body: bytes) -> 'AIxCCTask':
        ...
