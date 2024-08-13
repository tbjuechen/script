from .performer import Performer

class MultiYHPerformer(Performer):
    description = '组队御魂副本(魂十、魂土、魂王等)'
    '''多人御魂'''
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    def main_step(self):
        target_list = ['refuse.jpg','yys_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        self.find_and_touch(target_list)