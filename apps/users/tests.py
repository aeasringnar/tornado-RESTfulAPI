import os, sys, time, random
base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path,'apps'))
from apps.users.models import Auth, Group, User
from base.settings import async_db
from peewee_async import Manager

objects = Manager(async_db)

def create_init_data():
    '''
    生成初始化数据
    '''
    datas = [
        {
            'id': 1,
            'group_type': 'SuperAdmin',
            'group_type_cn': '超级管理员'
        },
        {
            'id': 2,
            'group_type': 'Admin',
            'group_type_cn': '管理员'
        },
        {
            'id': 3,
            'group_type': 'NormalUser',
            'group_type_cn': '普通用户'
        }
    ]
    Group.insert_many(datas).execute()
    User.insert(username='superadmin', password='123456', group=1).execute()

def test_insert_datas():
    '''
    测试批量插入数据
    '''
    auths = []
    str_ls = ['管理员', '超级管理员', '普通会员', '超级会员']
    for num in range(0, 100000):
        auth = random.choice(str_ls)
        auths.append({'auth_type': '%s%d' % (auth,num)})
    Auth.insert_many(auths).execute()

def del_datas():
    print('测试删除数据操作')

if __name__ == '__main__':
    start_time = time.time()
    create_init_data()
    print('耗时：', time.time() - start_time)