from __future__ import annotations

MAX_ZAGREB_PRICE_EUR = 240_000
MAX_ZAGREB_APARTMENT_PRICE_EUR = 300_000
MIN_ZAGREB_PRICE_EUR = 10_000
MAX_COAST_PRICE_EUR = 50_000
MIN_COAST_PRICE_EUR = 10_000
MIN_ZAGREB_HOUSE_SIZE_M2 = 90
MIN_ZAGREB_APARTMENT_LIVING_M2 = 55
MIN_ZAGREB_HOUSE_BUILD_YEAR = 2000
MIN_ZAGREB_APARTMENT_BUILD_YEAR = 2010

# Areas the monitor searches. Each entry is:
#   (display name, Njuškalo URL slug, Index location UUID)
# All entries are Index level 2 (city / municipality / Zagreb district).
WATCH_AREAS = (
    # Grad Zagreb
    ("Brezovica", "brezovica", "6bef087e-db1f-490b-af67-4d29677732ec"),
    ("Novi Zagreb - Istok", "novi-zagreb-istok", "37749e63-89a8-49af-ae25-c0cfcf6c9aff"),
    ("Novi Zagreb - Zapad", "novi-zagreb-zapad", "00a70eb0-4f43-45b1-9014-61732632251d"),
    ("Podsused - Vrapče", "podsused-vrapce", "d570ea3f-debe-409e-866b-dd3960ee6ba1"),
    ("Sesvete", "sesvete", "a89fa11b-0803-45fd-aec5-281053dab55d"),
    ("Stenjevec", "stenjevec", "9331f24f-e3ff-4a76-8ccc-971b3c3133d2"),
    ("Trešnjevka - Jug", "tresnjevka-jug", "77cb2e80-9c36-4282-aea3-b2c3b026f3e9"),
    ("Zagreb - Okolica", "zagreb-okolica", "f1278798-cbfc-4d76-97c5-65b676b0f983"),
    # Zagrebačka županija - gradovi
    ("Dugo Selo", "dugo-selo", "3ad3dab9-3abd-4ed4-90fa-f77c9de1b70a"),
    ("Ivanić-Grad", "ivanic-grad", "0b36f2a8-b3dd-4c2a-ac49-72e200e5a081"),
    ("Velika Gorica", "velika-gorica", "44491a41-be92-4dfa-824e-6e7dbdaa4f6f"),
    ("Zaprešić", "zapresic", "33670252-7421-44f2-81fa-c13e2d7c971f"),
    # Zagrebačka županija - općine
    ("Bistra", "bistra", "e454221c-a567-400f-8272-d228492e4980"),
    ("Kloštar Ivanić", "klostar-ivanic", "e4798117-4ed9-4a65-9697-cd43ca6c6890"),
    ("Rugvica", "rugvica", "6fe61262-c5ac-42e5-bc80-c5e1cfb9d632"),
    ("Stupnik", "stupnik", "bafc4cff-d259-473f-8af1-33ac72eda150"),
    # Zagrebačka županija - okolica
    ("Dugo Selo - Okolica", "dugo-selo-okolica", "2563c63b-3927-4435-952f-9a42b4b31627"),
    ("Ivanić-Grad - Okolica", "ivanic-grad-okolica", "326082e0-4a69-4681-b225-874ca50bbb8a"),
    ("Velika Gorica - Okolica", "velika-gorica-okolica", "42bd43b5-53b2-438c-b32e-d5a7dad8457c"),
)

WATCH_AREA_NAMES = tuple(name for name, _, _ in WATCH_AREAS)
WATCH_AREA_SLUGS = tuple(slug for _, slug, _ in WATCH_AREAS)
WATCH_AREA_INDEX_IDS = tuple(index_id for _, _, index_id in WATCH_AREAS)

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
