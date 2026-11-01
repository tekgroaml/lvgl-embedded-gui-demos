"""Explicit catalog: adding a scene does not add branches to the GTK worker."""
from .different.automotive_industrial.scene import SCENE as mixed
from .different.flight.scene import SCENE as flight
from .different.industrial.scene import SCENE as industrial
from .different.automotive.scene import SCENE as automotive
from .different.pc_monitor.scene import SCENE as pc_monitor
from demos.different.round.scene import SCENE as product_showcase
from .different.smart_home.scene import SCENE as smart_home
from .different.pc_monitor_square.scene import SCENE as pc_monitor_square
from demos.different.square.scene import SCENE as square_showcase
from .same.round.music_ambient.scene import SCENE as music_ambient
from .same.round.music_ambient.scene import CLONE_SCENE as music_ambient_clone
from .same.round.ambient_light.scene import SCENE as ambient_light,CLONE_SCENE as ambient_light_clone
from .same.round.ambient_clock.scene import SCENE as ambient_clock,CLONE_SCENE as ambient_clock_clone
from demos.same.round.scene import SCENE as same_showcase,SBS_SCENE as same_showcase_sbs
from .same.square.store_signage.scene import SCENE as store,CLONE_SCENE as store_clone
from .same.square.meeting_room.scene import SCENE as room,CLONE_SCENE as room_clone
from .same.square.parcel_status.scene import SCENE as parcel,CLONE_SCENE as parcel_clone
from demos.same.square.scene import SCENE as square_same,SBS_SCENE as square_same_sbs

_registered=(mixed,flight,industrial,automotive,pc_monitor,product_showcase,
             smart_home,pc_monitor_square,square_showcase,music_ambient,music_ambient_clone,
             ambient_light,ambient_light_clone,ambient_clock,ambient_clock_clone,
             same_showcase,same_showcase_sbs,store,store_clone,room,room_clone,
             parcel,parcel_clone,square_same,square_same_sbs)
DEFINITIONS={scene.id:scene for scene in _registered}
if len(DEFINITIONS)!=len(_registered):
    raise RuntimeError('Duplicate scene IDs')
LAYOUTS={f'{scene.prefix}-{size}':(scene,size) for scene in DEFINITIONS.values() for size in scene.sizes}
if len(LAYOUTS)!=sum(len(scene.sizes) for scene in _registered):
    raise RuntimeError('Duplicate layout IDs')

# Retained mapping shape for existing CLI/tool integrations.
SCENES={name:{'shapes':list(scene.shapes),'prefix':scene.prefix,'sources':list(scene.sources),
              'panels':list(scene.panel_ids),'content_modes':list(scene.content_modes)} for name,scene in DEFINITIONS.items()}


def definition(view):
    try:return DEFINITIONS[view]
    except (KeyError,TypeError):raise ValueError('Unknown scene') from None


def make_scene(view):
    scene=definition(view)
    return scene.create_panels(),scene.create_source()
