"""Official EIA Weekly Petroleum Status Report adapter."""
from __future__ import annotations
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from app.calendar.models.event import CalendarEvent, ImpactLevel
from app.calendar.official_sources.base import SourceDownloadError
from app.calendar.official_sources.bls import UrlLibTextClient
EIA_URL="https://www.eia.gov/petroleum/supply/weekly/"; EASTERN=ZoneInfo("America/New_York")
class EiaSource:
    name="EIA"
    def fetch(self, client: object|None=None)->list[CalendarEvent]:
        try: html=(client or UrlLibTextClient()).get_text(EIA_URL, timeout=20.0) # type: ignore[attr-defined]
        except Exception as error: raise SourceDownloadError(f"EIA WPSR download failed: {error}") from error
        return self.parse_schedule(html)
    def parse_schedule(self, html:str)->list[CalendarEvent]:
        text=" ".join(re.sub(r"<[^>]+>"," ",html).split()); found=re.search(r"Next Release Date:\s*([A-Z][a-z]+ \d{1,2}, \d{4})",text)
        if not found: raise SourceDownloadError("EIA next release date missing")
        when=datetime.strptime(found.group(1)+" 10:30 AM","%B %d, %Y %I:%M %p").replace(tzinfo=EASTERN)
        return [CalendarEvent(f"eia-crude-{when:%Y%m%d}","United States","Weekly Crude Oil Inventories",when,("WTI","Brent","USD"),"High","EIA",EIA_URL,ImpactLevel.HIGH,release_url=EIA_URL)]
    def parse_release(self, html:str)->tuple[str|None,str|None]:
        text=" ".join(re.sub(r"<[^>]+>"," ",html).split()); found=re.search(r"commercial crude oil inventories.*?(increased|decreased) by ([\d.]+) million barrels",text,re.I)
        if not found:return None,None
        return (("+" if found.group(1).lower()=="increased" else "-")+found.group(2)+"M",None)
