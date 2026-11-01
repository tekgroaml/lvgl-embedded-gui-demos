"""Square same-content capabilities with separate clone and SBS input mappings."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('store-signage','Square retail promotion',('square','square'),'store-signage-sbs',('store-signage','store-signage'),
                      ('scenes.same.square.store_signage.panels:StorePanel','scenes.same.square.store_signage.panels:StorePanel'),
                      'scenes.same.square.store_signage.model:StoreDemo',content_modes=('same',))
CLONE_SCENE=SceneDefinition('store-signage-clone','Hardware-cloned square retail promotion',SCENE.shapes,
                      'store-signage-clone',SCENE.panel_ids,SCENE.panel_factories,SCENE.demo_factory,
                      package='scenes.same.square.store_signage',content_modes=('same',),topology='single-link-clone')
