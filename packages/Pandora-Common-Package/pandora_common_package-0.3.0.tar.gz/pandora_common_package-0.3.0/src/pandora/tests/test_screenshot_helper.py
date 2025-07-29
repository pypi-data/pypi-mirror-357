import os
import pytest
import uuid
from src.pandora.utils.screenshot_helper import ScreenshotHelper
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class TestScreenshotHelper:
    def setup_method(self):
        """
        Reset value of self.screenshot_path to None before execution of each test method.
        """
        self.screenshot_path: str | None = None

    def teardown_method(self):
        """
        Reset value of ScreenshotHelper class field to default value before execution of each test method.
        If current method successfully capture a screenshot, then remove screenshot file.
        """
        ScreenshotHelper.max_screenshots = 100
        ScreenshotHelper.__screenshot_count__ = 0
        if self.screenshot_path:
            os.remove(self.screenshot_path)

    def generic_screenshot_assertion(self, assert_type: str):
        """
        Generic method for screenshot_assertion.
        Firstly assert for ScreenshotHelper.capture_screenshot() returns successful result (path of screenshot file).
        Secondly assert for target screenshot file exists.
        """
        assert self.screenshot_path, f"Capture screenshot by {assert_type} failed"
        assert os.path.isfile(
            self.screenshot_path), f"Save screenshot failed, file doesn't exist: {self.screenshot_path}"

    def generic_screenshot_assertion_failed(self, assert_type: str):
        """
        Generic method for screenshot_assertion with failure.
        Assert for ScreenshotHelper.capture_screenshot() returns failed result (None).
        """
        assert not self.screenshot_path, f"Expect capture screenshot by {assert_type} failed, but actually succeeded"

    def test_screenshot_by_default(self):
        self.screenshot_path = ScreenshotHelper.capture_screenshot()
        self.generic_screenshot_assertion(assert_type="default")

    # Check for relative path/absolute path/not exists path
    @pytest.mark.parametrize("screenshot_dir",
                             [["relative path", ".\\"],
                              ["absolute path", os.path.dirname(os.path.abspath(__file__))],
                              ["not exists path", f"./{str(uuid.uuid4())}"]])
    def test_screenshot_by_screenshot_dir(self, screenshot_dir):
        self.screenshot_path = ScreenshotHelper.capture_screenshot(screenshot_dir=screenshot_dir[1])
        self.generic_screenshot_assertion(assert_type=f"screenshot dir {screenshot_dir[0]}")

    def test_screenshot_by_file_prefix(self):
        self.screenshot_path = ScreenshotHelper.capture_screenshot(file_prefix="pandora_test")
        self.generic_screenshot_assertion(assert_type="file prefix")

    # Check for all supported file extension: .png/jpg/.jpeg/bmp/.gif, leading dots (.) will be stripped automatically
    @pytest.mark.parametrize("file_extension", [".png", "jpg", ".jpeg", "bmp", ".gif"])
    def test_screenshot_by_file_extension(self, file_extension):
        self.screenshot_path = ScreenshotHelper.capture_screenshot(file_extension=file_extension)
        self.generic_screenshot_assertion(assert_type=f"file extension {file_extension}")

    # Check for some unsupported file extension: .exe/rar
    @pytest.mark.parametrize("file_extension", [".exe", "rar"])
    def test_screenshot_by_file_extension_unsupported(self, file_extension):
        self.screenshot_path = ScreenshotHelper.capture_screenshot(file_extension=file_extension)
        self.generic_screenshot_assertion_failed(assert_type=f"file extension {file_extension}")

    def test_screenshot_over_limits(self):
        # Set limitation of max screenshots
        ScreenshotHelper.max_screenshots = 2

        # Capture screenshots succeeded before over limits
        for i in range(2):
            self.screenshot_path = ScreenshotHelper.capture_screenshot()
            self.generic_screenshot_assertion(assert_type="limitation")
            os.remove(self.screenshot_path)

        # Capture screenshots failed after over limits
        for i in range(2):
            self.screenshot_path = ScreenshotHelper.capture_screenshot()
            self.generic_screenshot_assertion_failed(assert_type="limitation")
