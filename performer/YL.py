from .performer import Performer

class YLPerformer(Performer):
    '''御灵'''
    description = '御灵副本'
    def __init__(self,**kwargs):
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','confirm.jpg','yuling_begin.jpg', 'yys_jieshu.jpg', 'yys_jixu.jpg']
        super().__init__(**kwargs)
    
    def main_step(self):
        self.find_and_touch(self.target_list)