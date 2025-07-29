from typing import Optional

from applitools.common import BatchInfo, RectangleSize, MatchLevel
from applitools.common.selenium import Configuration, BrowserType
from applitools.selenium import Eyes, VisualGridRunner


class AppliTool(object):

    def __init__(self, appli_key, appli_server, app_name):
        self.runner = (
            VisualGridRunner()
        )  #  runner = VisualGridRunner(concurrent_sessions=5)
        self.eyes = Eyes(self.runner)
        eye_config = self.eyes.get_configuration()
        eye_config.set_host_os("Windows 11")
        eye_config.set_host_app(app_name)
        eye_config.set_api_key(appli_key)
        eye_config.set_server_url(appli_server)
        eye_config.save_new_tests = True

        batch_info = BatchInfo("UI_Icicile_Batch1")
        # Optionally, set a unique batch ID
        batch_info.id = "icicle_001"
        batch_info.add_property("Environment", "stg")
        batch_info.add_property("Version", "5.2")
        # Assign the batch to the Eyes object
        eye_config.set_batch(batch_info)

        eye_config.match_level = MatchLevel.STRICT
        self.eyes.set_configuration(eye_config)
