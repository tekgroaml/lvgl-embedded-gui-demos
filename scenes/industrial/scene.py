"""Registration and supported features for the square pump-station scene."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('industrial','Dual-square pump station',('square','square'),'industrial-sbs',
                      ('pump','process-trends'),
                      ('scenes.industrial.panels:PumpPanel','scenes.industrial.panels:ProcessTrends'),
                      'scenes.industrial.model:ProcessDemo')
