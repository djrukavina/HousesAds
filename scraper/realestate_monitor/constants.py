from __future__ import annotations

MAX_ZAGREB_PRICE_EUR = 300_000
MAX_ZAGREB_APARTMENT_PRICE_EUR = 340_000
MIN_ZAGREB_PRICE_EUR = 10_000
MAX_COAST_PRICE_EUR = 50_000
MIN_COAST_PRICE_EUR = 10_000
MIN_ZAGREB_HOUSE_SIZE_M2 = 100
MIN_ZAGREB_APARTMENT_LIVING_M2 = 70
MIN_ZAGREB_APARTMENT_ROOMS = 3.0
MAX_ZAGREB_APARTMENT_ROOMS = 4.0

ZAGREB_CITY = (
    "zagreb",
    "podsused",
    "trešnjevka",
    "tresnjevka",
    "maksimir",
    "trnje",
    "črnomerec",
    "crnomerec",
    "stenjevec",
    "podsljeme",
    "brezovica",
    "novi zagreb",
    "donji grad",
    "gornji grad",
    "medveščak",
    "medvescak",
)

# Towns in Zagrebačka županija (apartments may be outside the city proper).
# Sesvete, Velika Gorica, Sveta Klara, Veliko Polje are excluded (see EXCLUDED_ZAGREB_AREAS).
ZAGREB_COUNTY = (
    "zagrebacka",
    "zagrebačka",
    "zapresic",
    "zaprešić",
    "samobor",
    "dugo selo",
    "sveta nedelja",
    "jastrebarsko",
    "ivanic-grad",
    "ivanić-grad",
    "ivanic grad",
    "ivanić grad",
    "vrbovec",
    "sveti ivan zelina",
    "zelina",
    "brdovec",
    "klinča sela",
    "klinca sela",
    "pisarovina",
    "bestovje",
    "lucko",
    "lučko",
    "kerestinec",
)

# Sesvete, Velika Gorica, Sveta Klara, Veliko Polje, and eastern Zagreb districts.
EXCLUDED_ZAGREB_AREAS = (
    "sesvete",
    "velika gorica",
    "sveta klara",
    "veliko polje",
    "kraljeveck",
    "kraljevečk",
    "markovo polje",
    "gajisce",
    "gajišće",
    "dubrava",
    "pescenica",
    "peščenica",
    "zitnjak",
    "žitnjak",
    "resnik",
    "borongaj",
    "istok zagreba",
)

HOUSE_LOCATIONS = (
    "zagreb",
    "samobor",
    "brezovica",
    "odra",
    "novi zagreb",
)

ISLANDS = (
    "krk",
    "cres",
    "lošinj",
    "losinj",
    "mali lošinj",
    "veli lošinj",
    "rab",
    "pag",
    "novalja",
    "brač",
    "brac",
    "hvar",
    "korčula",
    "korcula",
    "vis",
    "mljet",
    "šolta",
    "solta",
    "dugi otok",
    "ugljan",
    "pašman",
    "pasman",
    "čiovo",
    "ciovo",
    "vir",
    "murter",
    "lastovo",
    "iž",
    "silba",
    "unije",
    "susak",
    "ilovik",
    "žirje",
    "prvić",
    "prvic",
    "kaprije",
    "zlarin",
    "krapanj",
    "koločep",
    "kolocep",
    "lopud",
    "šipan",
    "sipan",
    "molat",
    "ist",
    "kornat",
    "žut",
    "rivanj",
    "sestrunj",
    "oliban",
    "otok",
)

ISLAND_URL_HINTS = (
    "/krk",
    "/cres",
    "/losinj",
    "/rab",
    "/pag",
    "/novalja",
    "/brac",
    "/hvar",
    "/korcula",
    "/vis",
    "/mljet",
    "/solta",
    "/dugi-otok",
    "/ugljan",
    "/pasman",
    "/ciovo",
    "/vir",
    "/murter",
    "/lastovo",
)

SEA_KEYWORDS = (
    "uz more",
    "do mora",
    "od mora",
    "blizina mora",
    "blizu mora",
    "pogled na more",
    "pogled more",
    "prvi red",
    "1. red",
    "1 red",
    "plaža",
    "plaza",
    "obala",
    "riviera",
    "marina",
    "lučica",
    "lucica",
    "uvali",
    "uvala",
)

NEW_BUILD_KEYWORDS = (
    "novogradnja",
    "nova gradnja",
    "u izgradnji",
    "novograd",
    "new build",
)
