import enum


class RecordType(enum.Enum):
    OHLCV_1S = 32
    OHLCV_1M = 33
    OHLCV_1H = 34
    OHLCV_1D = 35

    @classmethod
    def to_string(cls, rtype: int) -> str:
        match rtype:
            case cls.OHLCV_1S.value:
                return "1s bars"
            case cls.OHLCV_1M.value:
                return "1m bars"
            case cls.OHLCV_1H.value:
                return "1h bars"
            case cls.OHLCV_1D.value:
                return "1d bars"
            case _:
                return f"unknown ({rtype})"
