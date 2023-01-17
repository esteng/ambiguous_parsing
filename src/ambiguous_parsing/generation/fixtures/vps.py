
VISUAL_VPS = ["saw", "observed", "watched", "spied"]
TACTILE_VPS = ["picked up", "grabbed", "held", "lifted"]
AUDITORY_VPS = ["heard", "listened to"]
OTHER_VPS = ["chased", "followed", "called"]

INTRANSITIVE_VPS = ["ate", "drank", "slept", "walked", "left", "played", "moved", "drew", "napped"]


VPS = (VISUAL_VPS + TACTILE_VPS + AUDITORY_VPS + OTHER_VPS)
VPS_MAP = {k:k for k in VPS}
VPS_MAP['listened to'] = 'listened'
VPS_MAP['picked_up'] = 'picked_up'