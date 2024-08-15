from .performer import Performer

class ActivityPerformer(Performer):
    '''
    活动爬塔副本
    '''
    description = '活动爬塔副本'
    def __init__(self,**kwargs):
        self.img_path = 'wanted/'
        self.target_list = ['refuse.jpg','active_begin.jpg', 'yys_jixu.jpg', 'yys_jieshu.jpg']
        super().__init__(**kwargs)
    
    def main_step(self):
        self.find_and_touch(self.target_list)
