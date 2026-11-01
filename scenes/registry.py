"""Explicit catalog: adding a scene does not add branches to the GTK worker."""
from .automotive_industrial.scene import SCENE as mixed
from .flight.scene import SCENE as flight
from .industrial.scene import SCENE as industrial
from .automotive.scene import SCENE as automotive
from .pc_monitor.scene import SCENE as pc_monitor
from demos.product_showcase.scene import SCENE as product_showcase
from .smart_home.scene import SCENE as smart_home
from .pc_monitor_square.scene import SCENE as pc_monitor_square
from demos.square_showcase.scene import SCENE as square_showcase

_registered=(mixed,flight,industrial,automotive,pc_monitor,product_showcase,
             smart_home,pc_monitor_square,square_showcase)
DEFINITIONS={scene.id:scene for scene in _registered}
if len(DEFINITIONS)!=len(_registered):
    raise RuntimeError('Duplicate scene IDs')
LAYOUTS={f'{scene.prefix}-{size}':(scene,size) for scene in DEFINITIONS.values() for size in scene.sizes}
if len(LAYOUTS)!=sum(len(scene.sizes) for scene in _registered):
    raise RuntimeError('Duplicate layout IDs')

# Retained mapping shape for existing CLI/tool integrations.
SCENES={name:{'shapes':list(scene.shapes),'prefix':scene.prefix,'sources':list(scene.sources),
              'panels':list(scene.panel_ids)} for name,scene in DEFINITIONS.items()}


def definition(view):
    try:return DEFINITIONS[view]
    except (KeyError,TypeError):raise ValueError('Unknown scene') from None


def make_scene(view):
    scene=definition(view)
    return scene.create_panels(),scene.create_source()
