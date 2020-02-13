# Queries for webdev-style dashboard

from deephaven import *

numSyms = 5
numDays = 3
buckets = 30

# Running average function
def rAvg(vals):
    arr = jpy.array('double', vals.size())
    avg = 0.0

    for i in range(vals.size()):
        arr[i] = (i*arr[i-1] + vals.get(i))/(i+1) if i > 0 else vals.get(i)

    return arr

import deephaven.Calendars as Calendars
cal = Calendars.calendar('USNYSE')
cutoffDate = cal.previousBusinessDay(cal.currentDay(), numDays - 1)

# Get trade data (filter out exchange aggregate)
trades = db.i("FeedOS", "EquityTradeL1")\
    .where("Date >= cutoffDate")\
    .where("LocalCodeStr not in `SPY`")

# Bin by minute and rename columns
countAndVolumeData = trades.view("TimeBin = upperBin(Timestamp, buckets*MINUTE)", 
    "Sym = LocalCodeStr", "TradeCount = 1", "Shares = (int) Size",
    "Price", "Dollars = (int) (Size * Price)")\
    .lastBy("TimeBin", "Sym")

# Get distinct syms
syms = countAndVolumeData.selectDistinct("Sym").head(numSyms)

# Limit by distinct syms
symLim = countAndVolumeData.join(syms, "Sym", "")

# Get day start prices
startPrices = symLim.firstBy("Sym")

# Join to main data
joinStarts = symLim\
    .naturalJoin(startPrices, "Sym", "StartPrice = Price")\
    .updateView("PriceDiff = Price - StartPrice").headPct(0.97)

# Curr price plot by sym
currPricePlot = plt.plotBy("Price Change", joinStarts, "TimeBin", "PriceDiff", "Sym")\
    .chartTitle("Current price plot for " + str(numDays) + " days")\
    .xLabel("Time")\
    .yLabel("Price Change")\
    .show()

# Last-Value-Cache (need to grab value before as well in order to compare and then use heatmap on hidden column)
lvc = joinStarts.lastBy("Sym")\
    .view("Sym", "Price", "PriceDiff")\
    .sort("Sym")

# Apply rAvg function to price column
withRAvgs = joinStarts.by("Sym").update("cumAvgPrice = (double[])rAvg.call(new Object[]{Price})").ungroup()

