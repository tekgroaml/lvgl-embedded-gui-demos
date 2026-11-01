"""Registration and supported features for the square pump-station scene."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('industrial','Dual-square pump station',('square','square'),'industrial-sbs',
                      ('pump','process-trends'),
                      ('scenes.different.industrial.panels:PumpPanel','scenes.different.industrial.panels:ProcessTrends'),
                      'scenes.different.industrial.model:ProcessDemo',native_dual480=True,
                      layout_versions=((480,'1.1.0'),))
