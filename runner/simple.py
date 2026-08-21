from .base import FindListRunner


class Active(FindListRunner):
    name = "active"
    description = "月伴生活动"
    targets = ("refuse.jpg", "active_begin.jpg", "yys_jixu.jpg", "yys_jieshu.jpg")


class Mitama(FindListRunner):
    name = "mitama"
    description = "御魂副本（悲鸣/组队）"
    targets = (
        "refuse.jpg",
        "active_begin.jpg",
        "yys_begin.jpg",
        "yys_jieshu.jpg",
        "yys_jixu.jpg",
    )
    # 悲鸣单人挑战按钮位于右下角；限定搜索区域，避免同图标误触。
    target_regions = {"active_begin.jpg": (0.80, 0.65, 1.0, 1.0)}


class HeroExp(FindListRunner):
    name = "hero-exp"
    description = "英杰经验副本"
    targets = ("refuse.jpg", "yj_exp_begin.jpg", "yys_jieshu.jpg", "yys_jixu.jpg")


class Spirit(FindListRunner):
    name = "spirit"
    description = "御灵副本"
    targets = (
        "refuse.jpg",
        "confirm.jpg",
        "yuling_begin.jpg",
        "yys_jieshu.jpg",
        "yys_jixu.jpg",
    )


class Fire(FindListRunner):
    name = "fire"
    description = "业原火"
    targets = ("refuse.jpg", "yyh_begin.jpg", "yys_jieshu.jpg", "yys_jixu.jpg")


# Compatibility with the old misspelled public name.
HreoExp = HeroExp
