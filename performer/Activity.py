from .performer import Performer

class ActivityPerformer(Performer):
    '''
    活动爬塔副本
    '''
    description = '活动爬塔副本'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','active_begin.jpg', 'yys_jixu.jpg', 'yys_jieshu.jpg']
        self.target_list = [self.img_path + i for i in self.target_list]
    
    def main_step(self):
        self.find_and_touch(self.target_list)
