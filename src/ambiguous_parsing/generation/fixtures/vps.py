
VISUAL_VPS = ["saw", "observed", "watched", "spied"]
TACTILE_VPS = ["picked up", "grabbed", "held", "lifted"]
AUDITORY_VPS = ["heard", "listened to"]
OTHER_VPS = ["chased", "followed", "called"]

VPS = (VISUAL_VPS + TACTILE_VPS + AUDITORY_VPS + OTHER_VPS)
VPS = {k:k for k in VPS}
VPS['listened to'] = 'listened'
VPS['picked_up'] = 'picked_up'