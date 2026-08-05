# BLS calendar integration

AutoTrade-HUB's first live official calendar source is the United States Bureau
of Labor Statistics (BLS). It uses only BLS-owned resources:

- Schedule: `https://www.bls.gov/schedule/news_release/bls.ics`
- CPI release: `https://www.bls.gov/news.release/cpi.nr0.htm`
- PPI release: `https://www.bls.gov/news.release/ppi.nr0.htm`
- Employment Situation release: `https://www.bls.gov/news.release/empsit.nr0.htm`

## Schedule parsing

The BLS source downloads the official iCalendar feed with a 20-second timeout.
It retries network, HTTP, decoding, and timeout failures three times using one-
then two-second exponential backoff. The parser unfolds iCalendar lines, reads
`DTSTART` and `SUMMARY`, and keeps only Consumer Price Index, Producer Price
Index, and Employment Situation releases.

Those releases normalize to six AutoTrade-HUB events: Consumer Price Index,
Core CPI, Producer Price Index, Non-Farm Payrolls, Unemployment Rate, and
Average Hourly Earnings. Times remain timezone-aware in US Eastern time.

## Released values

The source reads the BLS release pages above. Regular expressions extract the
official headline value, and prior value where the release text provides it.
Missing or changed text returns no actual value; `fetch_release` then raises a
meaningful `SourceDownloadError` rather than sending a false release alert.
`fetch_released_event` returns a normalized `CalendarEvent` with its `actual`
and `previous` fields populated.

## Known limitations

- BLS does not publish market consensus forecasts, so `forecast` is empty.
- The supported actuals are headline text values; release-table revisions and
  alternate measures are not yet captured.
- HTML wording changes require parser fixture updates.
- The release pages are the current editions; historical event-to-release URL
  mapping is not yet persisted.
