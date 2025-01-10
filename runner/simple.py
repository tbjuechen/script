# simple task runner

from .base import FindListRunner

class active(FindListRunner):
    name = 'active'
    description = 'for monthly active'
    targets = ['refuse.jpg','active_begin.jpg', 'yys_jixu.jpg', 'yys_jieshu.jpg']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Mitama(FindListRunner):
    name = 'Mitama'
    description = 'for Mitama'
    targets =  ['refuse.jpg','yys_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)