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
    never = 0
    failed = 1
    refreshing = 2
    success = 3
