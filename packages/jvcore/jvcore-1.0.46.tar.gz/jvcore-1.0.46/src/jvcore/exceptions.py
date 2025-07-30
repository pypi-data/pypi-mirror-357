class ShutdownException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class CoreToolException(Exception):
    def __init__(self, coreToolName: str, *args: object) -> None:
        super().__init__(*args)
        
class ToolException(Exception):
    def __init__(self, toolName: str, *args: object) -> None:
        super().__init__(*args)
        
class SkillException(Exception):
    def __init__(self, skillName: str, *args: object) -> None:
        super().__init__(*args)
