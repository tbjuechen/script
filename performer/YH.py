from .performer import Performer

class MultiYHPerformer(Performer):
    '''多人御魂'''
    description = '组队御魂副本(魂十、魂土、魂王等)'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','yys_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        self.target_list = [self.img_path + i for i in self.target_list]
    
    def main_step(self):
        self.find_and_touch(self.target_list)