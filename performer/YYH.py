from .performer import Performer

class YYHPerformer(Performer):
    '''业原火'''
    description = '业原火副本'
    def __init__(self,**kwargs):
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','yyh_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        super().__init__(**kwargs)
    
    def main_step(self):
        self.find_and_touch(self.target_list)