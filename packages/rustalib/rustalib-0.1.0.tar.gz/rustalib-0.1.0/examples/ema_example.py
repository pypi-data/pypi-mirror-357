import pandas as pd
from rustalib import EMA

def main():
    # Load data from cvs
    df = pd.read_csv("examples/data/SPY_1D.csv")
    close_prices = df["Close"].tolist()

    # Create Exponential Moving Average (EMA) indicator
    ema = EMA(period=20)
    
    # Backtesting mode
    df["EMA20"] = ema.calculate_all(close_prices)

    # Imprimir las últimas filas
    print(df[["Date", "Close", "EMA20"]].tail())

if __name__ == "__main__":
    main()
