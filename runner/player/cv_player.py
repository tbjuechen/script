from __future__ import annotations

from pathlib import Path

import cv2
from loguru import logger

from .base import Player


class CVPlayer(Player):
    """OpenCV template matcher."""

    def __init__(
        self,
        acc: float = 0.8,
        reference_size: tuple[int, int] = (1920, 1080),
        **kwargs,
    ) -> None:
        super().__init__(acc=acc, **kwargs)
        self.reference_size = reference_size

    def load(self, path: str) -> cv2.typing.MatLike:
        image_path = Path(path)
        if not image_path.is_file():
            raise FileNotFoundError(f"无法读取图片：{path}")
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"无法读取图片：{path}")
        return image

    def locate(
        self,
        target: str,
        screenshot: str,
        debug: bool = False,
        region: tuple[float, float, float, float] | None = None,
    ) -> tuple[int, int] | None:
        target_img = self.load(target)
        screenshot_img = self.load(screenshot)
        screen_h, screen_w = screenshot_img.shape[:2]
        reference_w, reference_h = self.reference_size
        scale_x = screen_w / reference_w
        scale_y = screen_h / reference_h
        if abs(scale_x - 1) > 0.01 or abs(scale_y - 1) > 0.01:
            target_img = cv2.resize(
                target_img,
                None,
                fx=scale_x,
                fy=scale_y,
                interpolation=cv2.INTER_AREA if scale_x < 1 else cv2.INTER_CUBIC,
            )
            logger.debug(
                "按截图分辨率 {}x{} 缩放模板：{:.3f} x {:.3f}",
                screen_w,
                screen_h,
                scale_x,
                scale_y,
            )
        search_img = screenshot_img
        offset_x = offset_y = 0
        if region is not None:
            left, top, right, bottom = region
            if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
                raise ValueError("region must be normalized as left, top, right, bottom")
            offset_x, offset_y = int(screen_w * left), int(screen_h * top)
            crop_right, crop_bottom = int(screen_w * right), int(screen_h * bottom)
            search_img = screenshot_img[offset_y:crop_bottom, offset_x:crop_right]

        target_h, target_w = target_img.shape[:2]
        search_h, search_w = search_img.shape[:2]
        if target_h > search_h or target_w > search_w:
            logger.warning("模板尺寸大于截屏：{}", target)
            return None

        result = cv2.matchTemplate(search_img, target_img, cv2.TM_CCOEFF_NORMED)
        _, confidence, _, top_left = cv2.minMaxLoc(result)
        logger.debug("模板 {} 匹配度 {:.3f}", Path(target).name, confidence)
        if confidence < self.acc:
            return None

        top_left = (top_left[0] + offset_x, top_left[1] + offset_y)
        center = (top_left[0] + target_w // 2, top_left[1] + target_h // 2)
        if debug:
            bottom_right = (top_left[0] + target_w, top_left[1] + target_h)
            marked = screenshot_img.copy()
            cv2.rectangle(marked, top_left, bottom_right, (0, 0, 255), 2)
            cv2.imshow(f"result: {Path(target).name}", marked)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return center
