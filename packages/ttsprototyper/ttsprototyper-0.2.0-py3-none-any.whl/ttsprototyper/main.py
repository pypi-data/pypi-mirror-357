import abc
import enum
import logging
import pandas as pd
from ttsprototyper.ontology import RecordType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class TTSPrototyper(abc.ABC):

    def __init__(
        self, path_to_csv: str, filter_for_symbol: str = None, max_bars: int = None
    ):
        self._path_to_csv = path_to_csv
        self._filter_for_symbol = filter_for_symbol
        self._max_bars = max_bars

        self._market_data_df = pd.DataFrame()

    @staticmethod
    def set_log_level(level=logging.INFO):
        logger.setLevel(level)

    def load_data(self):
        try:
            self._market_data_df = pd.read_csv(
                self._path_to_csv,
                usecols=[
                    "ts_event",
                    "rtype",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "symbol",
                ],
                dtype={
                    "ts_event": int,
                    "rtype": int,
                    "open": int,
                    "high": int,
                    "low": int,
                    "close": int,
                    "volume": int,
                    "symbol": str,
                },
            )

            if self._filter_for_symbol is not None:
                self._market_data_df = self._market_data_df[
                    self._market_data_df["symbol"] == self._filter_for_symbol
                ]
                if self._market_data_df.empty:
                    raise ValueError(
                        f"No data found for symbol: {self._filter_for_symbol}"
                    )

            self._market_data_df["ts_event"] = pd.to_datetime(
                self._market_data_df["ts_event"], unit="ns"
            )
            self._market_data_df["open"] = self._market_data_df["open"] / 1e9
            self._market_data_df["high"] = self._market_data_df["high"] / 1e9
            self._market_data_df["low"] = self._market_data_df["low"] / 1e9
            self._market_data_df["close"] = self._market_data_df["close"] / 1e9

            # Apply max_bars limit if specified
            if self._max_bars is not None and self._max_bars > 0:
                self._market_data_df = self._market_data_df.head(self._max_bars)
                logger.info(f"Limited data to first {self._max_bars} bars as requested")

            _rtypes = self._market_data_df["rtype"].unique().tolist()
            if len(_rtypes) != 1:
                raise ValueError(f"Expected single rtype but found multiple: {_rtypes}")

            logger.info(
                f"Loaded {len(self._market_data_df)} "
                f"{RecordType.to_string(_rtypes[0])}, "
                f"time period: "
                f"{self._market_data_df['ts_event'].min()} to "
                f"{self._market_data_df['ts_event'].max()}."
            )
            logger.debug(
                f"Loaded market data to _market_data_df dataframe:\n"
                f"Note: The dataframe index might not correspond to the number set by "
                f"max_bars because a symbol filter was applied to exclude rows not "
                f"belonging to the requested symbol!\n{self._market_data_df}"
            )

        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            self._market_data_df = pd.DataFrame()
            raise e
