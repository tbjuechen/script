from .performer import Performer

class YJExpPerformer(Performer):
    '''英杰经验副本'''
    description = '英杰经验副本'
    def __init__(self,**kwargs):
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','yj_exp_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        super().__init__(**kwargs)