from .performer import Performer

class YYHPerformer(Performer):
    '''业原火'''
    description = '业原火副本'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','yyh_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        self.target_list = [self.img_path + i for i in self.target_list]
    
    def main_step(self):
        self.find_and_touch(self.target_list)