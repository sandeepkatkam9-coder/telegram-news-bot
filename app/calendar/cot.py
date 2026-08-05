"""Parser for official CFTC legacy COT CSV rows."""
from __future__ import annotations
import csv
from dataclasses import dataclass
from io import StringIO
@dataclass(frozen=True, slots=True)
class CotPosition:
    market:str; open_interest:int; commercial_long:int; commercial_short:int; large_speculators_long:int; large_speculators_short:int; retail_long:int; retail_short:int
def parse_legacy_csv(payload:str)->list[CotPosition]:
    markets={"GOLD - COMMODITY EXCHANGE INC.":"Gold","SILVER - COMMODITY EXCHANGE INC.":"Silver","CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE":"WTI","U.S. DOLLAR INDEX - ICE FUTURES U.S.":"USD Index"}; results=[]
    for row in csv.DictReader(StringIO(payload)):
        market=markets.get(row.get("Market_and_Exchange_Names", ""))
        if market: results.append(CotPosition(market,int(row["Open_Interest_All"]),int(row["Commercial_Positions_Long_All"]),int(row["Commercial_Positions_Short_All"]),int(row["Noncommercial_Positions_Long_All"]),int(row["Noncommercial_Positions_Short_All"]),int(row["Nonrept_Positions_Long_All"]),int(row["Nonrept_Positions_Short_All"])))
    return results
