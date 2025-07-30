from typing import List, Optional

# SMA
class SMA:
    """Simple Moving Average indicator."""

    def __init__(self, period: int) -> None:
        """Initialize SMA with the given period."""
        ...

    def next(self, value: float) -> Optional[float]:
        """Add a new value and calculate incremental SMA.

        Returns:
            The current SMA value or None if insufficient data.
        """
        ...

    def calculate_all(self, data: List[float]) -> List[Optional[float]]:
        """Calculate SMA for the entire data history.

        Args:
            data: List of floats representing price history.

        Returns:
            List of SMA values, None where undefined.
        """
        ...

    def value(self) -> Optional[float]:
        """Get the last calculated SMA value or None if unavailable."""
        ...

    def values(self) -> List[Optional[float]]:
        """Get all SMA values computed so far."""
        ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

# EMA
class EMA:
    """
    Exponential Moving Average (EMA) indicator.

    Computes the EMA using an incremental smoothing method.
    """

    def __init__(self, period: int) -> None:
        """
        Initialize the EMA indicator with a given period.

        Args:
            period (int): Number of periods for the smoothing calculation.
        """
        ...

    def next(self, value: float) -> Optional[float]:
        """
        Add a new price value and update the EMA.

        Args:
            value (float): New price input.

        Returns:
            Optional[float]: The updated EMA value or None if not enough data.
        """
        ...

    def calculate_all(self, data: List[float]) -> List[Optional[float]]:
        """
        Compute EMA values for an entire series of price data.

        Args:
            data (List[float]): List of prices.

        Returns:
            List[Optional[float]]: EMA values for each input price.
        """
        ...

    def value(self) -> Optional[float]:
        """Return the most recent EMA value, or None if not ready."""
        ...

    def values(self) -> List[Optional[float]]:
        """Return all calculated EMA values."""
        ...

    @property
    def period(self) -> int:
        """Return the configured EMA period."""
        ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

# MACD Output
class MACDOutput:
    """Represents a single MACD calculation result."""
    macd: float
    signal: float
    histogram: float

    def __init__(self, macd: float, signal: float, histogram: float) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

# MACD
class MACD:
    """
    MACD indicator (Moving Average Convergence Divergence).

    Calculates the MACD line, signal line, and histogram using exponential moving averages (EMAs).
    """

    def __init__(self, fast_period: int, slow_period: int, signal_period: int) -> None:
        """
        Create a new MACD indicator with specified EMA periods.

        Args:
            fast_period (int): Period for the fast EMA (commonly 12).
            slow_period (int): Period for the slow EMA (commonly 26).
            signal_period (int): Period for the signal line EMA (commonly 9).
        """
        ...

    def next(self, value: float) -> Optional[MACDOutput]:
        """
        Process the next price value incrementally.

        Args:
            value (float): The new price value.

        Returns:
            Optional[MACDOutput]: MACD result if enough data has been processed, otherwise None.
        """
        ...

    def calculate_all(self, data: List[float]) -> List[Optional[MACDOutput]]:
        """
        Calculate the MACD indicator for an entire historical data series.

        Args:
            data (List[float]): A list of price values.

        Returns:
            List[Optional[MACDOutput]]: A list of MACD results or None for insufficient data.
        """
        ...

    def value(self) -> Optional[MACDOutput]:
        """
        Get the most recent MACD value.

        Returns:
            Optional[MACDOutput]: Latest MACD result or None if not available.
        """
        ...

    def values(self) -> List[Optional[MACDOutput]]:
        """
        Get all computed MACD values.

        Returns:
            List[Optional[MACDOutput]]: History of MACD results.
        """
        ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
