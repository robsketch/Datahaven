from deephaven import *
import deephaven.Calendars as Calendars
cal = Calendars.calendar("USNYSE")
date1 = cal.previousBusinessDay(cal.currentDay(), 3)

t1 = db.i("FeedOS", "EquityTradeL1")\
    .where("Date>=date1")

tradesBy15MinBySym = t1.view("TimeBin = upperBin(Timestamp,'00:05:00')","Sym = LocalCodeStr",\
    "Shares = (int) Size", "Price","Date")\
    .lastBy("TimeBin","Sym").sortDescending("TimeBin")

multiplePlot = plt.plot("PFE", tradesBy15MinBySym.where("Sym = `AAPL`"), "TimeBin", "Price")\
   .plot("CSCO", tradesBy15MinBySym.where("Sym = `MSFT`"), "TimeBin", "Price")\
   .plot("A", tradesBy15MinBySym.where("Sym = `A`"), "TimeBin", "Price")\
   .plot("SPY", tradesBy15MinBySym.where("Sym = `SPY`"), "TimeBin", "Price")\
   .xLabel("Time")\
   .yLabel("Price")\
   .show()

tradesMaxMin = tradesBy15MinBySym.by(caf.AggCombo(
    caf.AggMax("MaxPrice=Price"),
    caf.AggMin("MinPrice=Price"),
    ), "Sym")

Downsampler = jpy.get_type("com.illumon.iris.downsampling.Downsampler")
downsampledTrades = Downsampler.downsample(db, t1, "Timestamp", "00:05:00", "LocalCodeStr")\
   .last("Price","Size")\
   .sum("Volume=Size")\
   .min("Low=Price")\
   .max("High=Price")\
   .execute()

# Sym Volatility

symVolatility = t1.view("Sym = LocalCodeStr", "Volatility = Price", "Date")\
    .stdBy("Date","Sym")\
    .where("Sym in `SPY`, `QQQ`, `IWM`, `GOOG`")

categoryPlotStacked = plt.catPlot("GOOG", symVolatility.where("Sym = `GOOG`"), "Date", "Volatility") \
    .catPlot("SPY", symVolatility.where("Sym = `SPY`"), "Date", "Volatility") \
    .catPlot("QQQ", symVolatility.where("Sym = `QQQ`"), "Date", "Volatility") \
    .catPlot("IWM", symVolatility.where("Sym = `IWM`"), "Date", "Volatility") \
    .chartTitle("Daily Price Volatility") \
    .show()

