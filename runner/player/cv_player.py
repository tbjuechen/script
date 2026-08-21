from __future__ import annotations

from pathlib import Path

import cv2
from loguru import logger

from .base import Player


class CVPlayer(Player):
    """OpenCV template matcher."""

    def load(self, path: str) -> cv2.typing.MatLike:
        image_path = Path(path)
        if not image_path.is_file():
            raise FileNotFoundError(f"无法读取图片：{path}")
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"无法读取图片：{path}")
        return image

    def locate(
        self, target: str, screenshot: str, debug: bool = False
    ) -> tuple[int, int] | None:
        target_img = self.load(target)
        screenshot_img = self.load(screenshot)
        target_h, target_w = target_img.shape[:2]
        screen_h, screen_w = screenshot_img.shape[:2]
        if target_h > screen_h or target_w > screen_w:
            logger.warning("模板尺寸大于截屏：{}", target)
            return None

        result = cv2.matchTemplate(screenshot_img, target_img, cv2.TM_CCOEFF_NORMED)
        _, confidence, _, top_left = cv2.minMaxLoc(result)
        logger.debug("模板 {} 匹配度 {:.3f}", Path(target).name, confidence)
        if confidence < self.acc:
            return None

        center = (top_left[0] + target_w // 2, top_left[1] + target_h // 2)
        if debug:
            bottom_right = (top_left[0] + target_w, top_left[1] + target_h)
            marked = screenshot_img.copy()
            cv2.rectangle(marked, top_left, bottom_right, (0, 0, 255), 2)
            cv2.imshow(f"result: {Path(target).name}", marked)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return center
