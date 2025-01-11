# simple task runner

from .base import FindListRunner

class Active(FindListRunner):
    name = 'active'
    description = '月伴生活动'
    targets = ['refuse.jpg','active_begin.jpg', 'yys_jixu.jpg', 'yys_jieshu.jpg']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Mitama(FindListRunner):
    name = 'Mitama'
    description = '多人御魂副本'
    targets =  ['refuse.jpg','yys_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class HreoExp(FindListRunner):
    name = 'HeroExp'
    description = '英杰经验副本'
    targets = ['refuse.jpg','yj_exp_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Spirit(FindListRunner):
    name = 'Spirit'
    description = '御灵副本'
    targets = ['refuse.jpg','confirm.jpg','yuling_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Fire(FindListRunner):
    name = 'Fire'
    description = '业原火'
    targets = ['refuse.jpg','yyh_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)