from .performer import Performer

class YYHPerformer(Performer):
    description = '业原火副本'
    '''业原火'''
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    def main_step(self):
        target_list = ['refuse.jpg','yyh_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        self.find_and_touch(target_list)