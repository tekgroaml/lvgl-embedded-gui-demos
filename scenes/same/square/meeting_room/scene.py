"""Square same-content capabilities with separate clone and SBS input mappings."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('meeting-room','Square meeting-room status',('square','square'),'meeting-room-sbs',('meeting-room','meeting-room'),
                      ('scenes.same.square.meeting_room.panels:RoomPanel','scenes.same.square.meeting_room.panels:RoomPanel'),
                      'scenes.same.square.meeting_room.model:RoomDemo',content_modes=('same',))
CLONE_SCENE=SceneDefinition('meeting-room-clone','Hardware-cloned square meeting-room status',SCENE.shapes,
                      'meeting-room-clone',SCENE.panel_ids,SCENE.panel_factories,SCENE.demo_factory,
                      package='scenes.same.square.meeting_room',content_modes=('same',),topology='single-link-clone',
                      refresh_overrides=((480,(60,62.811001)),),layout_versions=((480,'1.1.0'),))
