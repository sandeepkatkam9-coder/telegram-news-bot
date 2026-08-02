"""

AutoTrade-HUB Market Event Database



Each event defines:



- keywords

- category

- importance

- urgency

- affected markets

"""



MARKET_EVENTS = {



    # =====================================================
# FEDERAL RESERVE
# =====================================================

"Fed Rate Decision": {
    "keywords": [
        "fomc",
        "rate decision",
        "interest rate decision",
        "fed rate decision"
    ],
    "category": "Central Bank",
    "importance": 100,
    "urgency": "Immediate",
    "markets": ["Gold", "USD", "EUR", "GBP", "Bitcoin"]
},

"FOMC Minutes": {
    "keywords": [
        "fomc minutes",
        "meeting minutes"
    ],
    "category": "Central Bank",
    "importance": 90,
    "urgency": "Immediate",
    "markets": ["Gold", "USD", "EUR"]
},

"Fed Chair Speech": {
    "keywords": [
        "kevin warsh",
        "fed chair",
        "federal reserve chair"
    ],
    "category": "Central Bank",
    "importance": 95,
    "urgency": "Immediate",
    "markets": ["Gold", "USD", "EUR", "GBP"]
},

"Fed Governor Speech": {
    "keywords": [
        "barkin",
        "waller",
        "bowman",
        "cook",
        "jefferson",
        "williams"
    ],
    "category": "Central Bank",
    "importance": 90,
    "urgency": "Immediate",
    "markets": ["Gold", "USD"]
},

"RBI Policy": {
    "keywords": [
        "rbi",
        "reserve bank of india",
        "repo rate",
        "monetary policy committee"
    ],
    "category": "Central Bank",
    "importance": 85,
    "urgency": "Immediate",
    "markets": ["USD", "Gold"]
},


    # =====================================================

    # INFLATION

    # =====================================================



    "CPI": {

        "keywords": [
    "cpi",
    "consumer price index",
    "inflation",
    "inflation rate"
],

        "category": "Inflation",

        "importance": 95,

        "urgency": "Immediate",

        "markets": ["Gold", "USD"]

    },



    "PPI": {

        "keywords": [

            "producer price index",

            "ppi"

        ],

        "category": "Inflation",

        "importance": 85,

        "urgency": "Immediate",

        "markets": ["Gold", "USD"]

    },



    "Core PCE": {

        "keywords": [

            "core pce",

            "pce inflation"

        ],

        "category": "Inflation",

        "importance": 95,

        "urgency": "Immediate",

        "markets": ["Gold", "USD"]

    },



    # =====================================================

    # EMPLOYMENT

    # =====================================================



    "NFP": {

        "keywords": [

            "nonfarm payrolls",

            "nfp"

        ],

        "category": "Employment",

        "importance": 95,

        "urgency": "Immediate",

        "markets": ["Gold", "USD"]

    },



    "Jobless Claims": {

        "keywords": [

            "jobless claims",

            "initial claims"

        ],

        "category": "Employment",

        "importance": 70,

        "urgency": "Today",

        "markets": ["Gold", "USD"]

    },



    # =====================================================

    # GROWTH

    # =====================================================



    "GDP": {

        "keywords": [

            "gdp",

            "gross domestic product"

        ],

        "category": "Growth",

        "importance": 85,

        "urgency": "Today",

        "markets": ["USD", "Gold"]

    },



    "PMI": {

        "keywords": [
    "pmi",
    "manufacturing pmi",
    "services pmi",
    "purchasing managers index"
],

        "category": "Growth",

        "importance": 70,

        "urgency": "Today",

        "markets": ["USD", "EUR", "GBP"]

    },



    # =====================================================

    # ENERGY

    # =====================================================



    "OPEC+": {

        "keywords": [
    "opec",
    "opec+",
    "oil production",
    "production cut",
    "production increase",
    "oil output"
],

        "category": "Energy",

        "importance": 90,

        "urgency": "Immediate",

        "markets": ["Oil", "Gold", "USD"]

    },



    "Crude Oil Inventories": {

        "keywords": [

            "crude inventories",

            "eia"

        ],

        "category": "Energy",

        "importance": 70,

        "urgency": "Today",

        "markets": ["Oil"]

    },



    # =====================================================

    # PRECIOUS METALS

    # =====================================================



    "Central Bank Gold": {

        "keywords": [

            "gold reserves",

            "gold purchases",

            "central bank gold"

        ],

        "category": "Precious Metals",

        "importance": 80,

        "urgency": "Today",

        "markets": ["Gold"]

    },



    # =====================================================

    # CRYPTO

    # =====================================================



    "Bitcoin ETF": {

        "keywords": [

            "bitcoin etf",

            "spot bitcoin etf"

        ],

        "category": "Crypto",

        "importance": 90,

        "urgency": "Immediate",

        "markets": ["Bitcoin"]

    },



    "Exchange Hack": {

        "keywords": [

            "exchange hack",

            "wallet hack",

            "crypto hack"

        ],

        "category": "Crypto",

        "importance": 80,

        "urgency": "Immediate",

        "markets": ["Bitcoin"]

    },



    # =====================================================

    # GEOPOLITICS

    # =====================================================



    "War": {

        "keywords": [

            "war",

            "missile",

            "airstrike",

            "military"

        ],

        "category": "Geopolitics",

        "importance": 90,

        "urgency": "Immediate",

        "markets": ["Gold", "Oil", "USD"]

    },



    "Sanctions": {

        "keywords": [

            "sanctions",

            "trade sanctions"

        ],

        "category": "Geopolitics",

        "importance": 80,

        "urgency": "Immediate",

        "markets": ["Gold", "Oil", "USD"]

    }

}
