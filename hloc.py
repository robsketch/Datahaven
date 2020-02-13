tempDate = "2019-10-17"
import deephaven.Calendars as Calendars
cal = Calendars.calendar("USNYSE")

#Get last 10 days of data
date = cal.previousBusinessDay(cal.currentDay(), 10)

# db.t for static data db.i for live
bizData = db.t("FeedOS","EquityTradeL1").where("Date = tempDate","InternalCode = 1059068156", "cal.isBusinessTime(MarketTimestamp)",\
#bizData = db.i("FeedOS","EquityTradeL1").where("Date = currentDateNy()","InternalCode = 1059068156", "cal.isBusinessTime(MarketTimestamp)",\
    "!isNull(Price)", "Price*100 % 1 == 0", "inRange(Size, 100.0, 10000.0)")\
    .renameColumns("Sym = LocalCodeStr")\
    .sort("Date", "MarketTimestamp")

Downsampler = jpy.get_type("com.illumon.iris.downsampling.Downsampler")

downsampledTrades = Downsampler.downsample(db, bizData, "MarketTimestamp", "00:05:00", "Sym")\
.first("Open = Price")\
.last("Close = Price")\
.min("Low=Price")\
.max("High=Price")\
.execute()

from deephaven import *
# ohlcPlot = plt.ohlcPlot("SPY", downsampledTrades, "MarketTimestamp", "Open", "High", "Low","Close")\
#      .chartTitle("SPY")\
#      .show()

# built-in ohlc plot functionality
ohlcPlot = plt.ohlcPlot("SPY", downsampledTrades, "MarketTimestamp", "Open", "High", "Low","Close")\
    .chartTitle("SPY")\
    .xBusinessTime()\
    .show()

wtf = db.t("FeedOS","EquityTradeL1").where("Date = `2019-10-04`","InternalCode = 1059068156", "inRange(MarketTimestamp, '2019-10-04T15:45:00 NY', '2019-10-04T15:50:00 NY')")