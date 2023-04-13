
VISUAL_VPS = ["saw", "observed", "spotted", "spied"]
TACTILE_VPS = ["picked up", "grabbed", "held", "lifted"]
AUDITORY_VPS = ["heard", "listened to"]
OTHER_VPS = ["chased", "followed", "called"]

TRANSITIVE_VPS = VISUAL_VPS + TACTILE_VPS # + AUDITORY_VPS # + OTHER_VPS
INTRANSITIVE_VPS = ["ate", "drank", "slept", "walked", "left", "played", "moved", "drew", "napped"]
INTRANSITIVE_VPS_FOR_BOUND = ["waved", "smiled", "lept", "frowned", "shouted"]

VPS = (VISUAL_VPS + TACTILE_VPS + AUDITORY_VPS + OTHER_VPS + INTRANSITIVE_VPS + INTRANSITIVE_VPS_FOR_BOUND)
VPS_MAP = {k:k for k in VPS}
VPS_MAP['listened to'] = 'listened'
VPS_MAP['picked up'] = 'picked_up'