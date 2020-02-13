from deephaven import *
import deephaven.Calendars as Calendars
cal = Calendars.calendar("USNYSE")
date1 = cal.previousBusinessDay(cal.currentDay(), 3)

# create initial trades table
t1 = db.i("FeedOS", "EquityTradeL1")\
    .where("Date>=date1")\
    .sortDescending("Timestamp")

# bucket trades by 15 minutes and rename columns
tradesBy15MinBySym = t1.view("TimeBin = upperBin(Timestamp,'00:05:00')","Sym = LocalCodeStr",\
    "Shares = (int) Size", "Price")\
    .lastBy("TimeBin","Sym").sortDescending("TimeBin")

# plot multiple syms on the same chart
multiplePlot = plt.plot("AAPL", tradesBy15MinBySym.where("Sym = `AAPL`"), "TimeBin", "Price")\
   .plot("MSFT", tradesBy15MinBySym.where("Sym = `MSFT`"), "TimeBin", "Price")\
   .plot("A", tradesBy15MinBySym.where("Sym = `A`"), "TimeBin", "Price")\
   .plot("SPY", tradesBy15MinBySym.where("Sym = `SPY`"), "TimeBin", "Price")\
   .xLabel("Time")\
   .yLabel("Price")\
   .show()

# get max and min price every 15 minutes from trades table
tradesMaxMin = tradesBy15MinBySym.by(caf.AggCombo(
    caf.AggMax("MaxPrice=Price"),
    caf.AggMin("MinPrice=Price"),
    ), "Sym")

# test out downsampler functionality on trades table
downsampledTrades = Downsampler.builder(db, t1, "Timestamp", "00:05:00", "LocalCodeStr")\
   .last("Price")\
   .sum("Volume=Size")\
   .min("Low=Price")\
   .max("High=Price")\
   .execute()


