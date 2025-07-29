import os
from datetime import datetime
from pyautogui import screenshot
from typing_extensions import Optional
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


class ScreenshotHelper:
    __screenshot_count__: int = 0
    max_screenshots: Optional[int] = None # None type means no limit of max screenshots

    @classmethod
    def capture_screenshot(cls, screenshot_dir: str = "./",
                           file_prefix: str = "screenshot",
                           file_extension: str = "png") -> Optional[str]:
        """
        Capture a system screenshot and save it to a timestamped file under a date-based subdirectory.

        This method will:
          1. Increment the internal screenshot counter and, if the limit (max_screenshots) is exceeded,
             skip taking a screenshot and return None.
          2. Build a target path of the form:
               {screenshot_dir}/{YYYYMMDD}/{file_prefix}_{YYYYMMDD_HHMMSSfff}.{file_extension}
             where:
               - YYYYMMDD is the current date (year, month, day).
               - HHMMSSfff is hours, minutes, seconds, and milliseconds.
             Any leading dots in `file_extension` are stripped, and it is lowercased.
          3. Create the date-based subdirectory if it does not already exist.
          4. Take a screenshot of the current screen and save it to the constructed path.
          5. Log the result (info on success, warning if over limit, error on failure).

        Args:
            screenshot_dir (str, optional):
                The root directory under which to create a date-based subfolder.
                Defaults to the current working directory ("./").
            file_prefix (str, optional):
                The prefix to use for the screenshot filename. Defaults to "screenshot".
            file_extension (str, optional):
                The desired image file extension (e.g: .png/jpg/.jpeg/bmp/.gif).
                Any leading dot (.) will be stripped automatically, and the remainder
                will be converted to lowercase. Defaults to "png".

        Returns:
            Optional[str]:
                - On success: the full file path (including directory, filename, and extension)
                  of the saved screenshot (e.g., "./20250603/screenshot_20250603_143507123.png").
                - If the internal screenshot limit (max_screenshots) has been exceeded: `None`.
                - If any exception occurs during directory creation or file saving: `None`.

        Examples:
            >>> ScreenshotHelper.max_screenshots = 25 # Optional, only if max_screenshots need to be reset
            ... path = ScreenshotHelper.capture_screenshot(
            ...     screenshot_dir="/tmp/screenshots",
            ...     file_prefix="test_run",
            ...     file_extension=".jpg"
            ... )
        """
        # Skip if trigger screenshots over limits
        cls.__screenshot_count__ += 1
        if cls.max_screenshots is not None and cls.__screenshot_count__ > cls.max_screenshots:
            logger.warning(f"Trigger screenshot over {cls.max_screenshots} times limits, skip actions!")
            return None

        try:
            # Handle screenshot file path
            current_datetime = datetime.now()
            timestamp = current_datetime.strftime('%Y%m%d_%H%M%S%f')[:-3]
            date_timestamp = current_datetime.strftime('%Y%m%d')
            file_extension = file_extension.lstrip('.').lower()  # Remove all of started `.` in file_extension
            filepath = os.path.join(screenshot_dir, date_timestamp, f"{file_prefix}_{timestamp}.{file_extension}")
            os.makedirs(os.path.join(screenshot_dir, date_timestamp), exist_ok=True)

            # Capture screenshot and save to path
            screenshot().save(filepath)
            logger.info(f"Screenshot saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error occurred while capturing screenshot: {e}")
            return None
