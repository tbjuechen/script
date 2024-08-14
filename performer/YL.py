from .performer import Performer

class YLPerformer(Performer):
    '''御灵'''
    description = '御灵副本'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','yuling_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        self.target_list = [self.img_path + i for i in self.target_list]
    
    def main_step(self):
        self.find_and_touch(self.target_list)