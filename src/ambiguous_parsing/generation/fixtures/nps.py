NAMES = ["Galileo", "Marie", "Sherlock", "Ada", "Alan", "Katherine", "Watson", "Adele", "Bill"]

INDEFINITE_HUMAN_NPS = ["boy", "girl", "man", "woman"]
INDEFINITE_NONHUMAN_SENTIENT_NPS = ["bird", "cat", "dog", "fish", "cow", "elephant"]
INDEFINITE_NONHUMAN_NONSENTIENT_NPS = ["book", "rock", "table", "cup", "crayon"]

VISUAL_INSTRUMENT_NPS = ["telescope", "pair of binoculars", "camera", "spyglass"]
TACTILE_INSTRUMENT_NPS = ["gloves", "mittens", "ovenmitts"]
CLOTHING_NPS = ["pyjamas", "pants", "sweater", "hat"]

INDEFINITE_NPS = (INDEFINITE_HUMAN_NPS + 
                  INDEFINITE_NONHUMAN_SENTIENT_NPS + 
                  INDEFINITE_NONHUMAN_NONSENTIENT_NPS +
                    VISUAL_INSTRUMENT_NPS +
                    TACTILE_INSTRUMENT_NPS +
                    CLOTHING_NPS)

INDEFINITE_NPS = {k:k for k in INDEFINITE_NPS}
# shorten to one word for meta language 
INDEFINITE_NPS['pair of binoculars'] = 'binoculars'
NPS = {k:v for k,v in INDEFINITE_NPS.items()}
NPS.update({k:k for k in NAMES})

# just for testing 
# INDEFINITE_NPS['boy'] = ['boy', 'child']

INDEFINITE_AMBIGUOUS = {"bank": ['bank_river', 'bank_money']}

