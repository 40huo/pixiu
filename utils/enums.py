from enum import Enum, unique


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)


@unique
class ResourceRefreshStatus(ChoiceEnum):
    """
    订阅源刷新状态
    """
    NEVER = 0
    FAIL = 1
    RUNNING = 2
    SUCCESS = 3
