import pandas as pd
from rustalib import SMA

def main():
    
    # Load data from cvs
    df = pd.read_csv("examples/data/SPY_1D.csv")
    close_prices = df["Close"].tolist()
    
    # Create Simple Moving Average (SMA) indicator
    sma = SMA(20)

    # Backtesting mode
    df["SMA20"] = sma.calculate_all(close_prices)

    # Imprimir las últimas filas
    print(df[["Date", "Close", "SMA20"]].tail())

if __name__ == "__main__":
    main()
