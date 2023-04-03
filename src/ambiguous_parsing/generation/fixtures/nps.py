NAMES = ["Galileo", "Marie", "Sherlock", "Ada", "Alan", "Katherine", "Watson", "Adele", "Bill", "Mary"]
MALE_NAMES = ["Galileo", "Sherlock", "Alan", "Watson", "Bill"]
FEMALE_NAMES = ["Marie", "Ada", "Katherine", "Adele", "Mary"]
INDEFINITE_HUMAN_NPS = ["boy", "girl", "man", "woman"]
INDEFINITE_MALE_NPS = ["boy", "man"]
INDEFINITE_FEMALE_NPS = ["woman", "girl"]

INDEFINITE_NONHUMAN_SENTIENT_NPS = ["bird", "cat", "dog", "fish", "cow", "elephant"]
INDEFINITE_NONHUMAN_NONSENTIENT_NPS = ["book", "rock", "table", "cup", "crayon"]

VISUAL_INSTRUMENT_NPS = ["telescope", "binoculars", "camera", "spyglass"]
TACTILE_INSTRUMENT_NPS = ["gloves", "mittens", "ovenmitts"]
CLOTHING_NPS = ["pyjamas", "pants", "sweater", "hat"]

NONVISUAL_NPS = TACTILE_INSTRUMENT_NPS + CLOTHING_NPS

INDEFINITE_NPS = (INDEFINITE_HUMAN_NPS + 
                  INDEFINITE_NONHUMAN_SENTIENT_NPS + 
                  INDEFINITE_NONHUMAN_NONSENTIENT_NPS +
                    VISUAL_INSTRUMENT_NPS +
                    TACTILE_INSTRUMENT_NPS +
                    CLOTHING_NPS)

INDEFINITE_SENTIENT_NPS = INDEFINITE_NONHUMAN_SENTIENT_NPS + INDEFINITE_HUMAN_NPS

INDEFINITE_NPS_MAP = {k:k for k in INDEFINITE_NPS}
# shorten to one word for meta language 
# INDEFINITE_NPS_MAP['pair of binoculars'] = 'binoculars'
NPS_MAP = {k:v for k,v in INDEFINITE_NPS_MAP.items()}
NPS_MAP.update({k:k for k in NAMES})

# INDEFINITE_AMBIGUOUS_MAP = {"bank": ['bank_river', 'bank_money']}

PLURAL_NP_TO_SINGULAR = {"pyjamas": "set of pyjamas",
                        "pants": "pair of pants",
                        "binoculars": "pair of binoculars",
                        "mittens": "pair of mittens",
                        "ovenmitts": "pair of ovenmitts",
                        "gloves": "pair of gloves"}

# LF has plural forms even for singular nouns 
for p, s in PLURAL_NP_TO_SINGULAR.items():
  INDEFINITE_NPS_MAP[s] = p
