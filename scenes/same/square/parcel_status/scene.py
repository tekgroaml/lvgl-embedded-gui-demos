"""Square same-content capabilities with separate clone and SBS input mappings."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('parcel-status','Square parcel pickup status',('square','square'),'parcel-status-sbs',('parcel-status','parcel-status'),
                      ('scenes.same.square.parcel_status.panels:ParcelPanel','scenes.same.square.parcel_status.panels:ParcelPanel'),
                      'scenes.same.square.parcel_status.model:ParcelDemo',content_modes=('same',))
CLONE_SCENE=SceneDefinition('parcel-status-clone','Hardware-cloned square parcel pickup status',SCENE.shapes,
                      'parcel-status-clone',SCENE.panel_ids,SCENE.panel_factories,SCENE.demo_factory,
                      package='scenes.same.square.parcel_status',content_modes=('same',),topology='single-link-clone')
