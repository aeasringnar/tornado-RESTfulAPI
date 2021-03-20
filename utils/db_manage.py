# 设置模块路径，否则 apps 无法导入
import os, sys
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path,'apps'))
from peewee import MySQLDatabase
from apps.users.models import User, Group, Auth, AuthPermission
# from users.models import User
from base.settings import sync_db
from playhouse.migrate import *


def run_create():
    '''生成表'''
    sync_db.connect()
    # sync_db.create_tables([UserProfile]) # 注意：如果检查没问题后数据库仍然报 (1215, 'Cannot add foreign key constraint') 那么需要使用下面的方式创建表，具体报错原因未知，可能create_tables内执行顺序不一致
    # UserProfile.create_table()
    Group.create_table()
    Auth.create_table()
    AuthPermission.create_table()
    User.create_table()
    sync_db.close()

def run_update():
    '''修改表'''
    sync_db.connect()
    migrator = MySQLMigrator(sync_db)
    # 由于peewee没办法像Django ORM那样迁移数据，因此如果在表创建好了之后还要对表字段做操作，就必须依靠peewee的migrate来操作了
    # 具体文档：http://docs.peewee-orm.com/en/latest/peewee/playhouse.html?highlight=migrate#example-usage
    # 下面的示例是用来修改表字段的名称，将多个表的add_time字段改为create_time字段
    with sync_db.atomic():
        migrate(
            migrator.rename_column('userprofile', 'add_time', 'create_time'),
            migrator.rename_column('verifyemailcode', 'add_time', 'create_time'),
            migrator.rename_column('category', 'add_time', 'create_time'),
            migrator.rename_column('post', 'add_time', 'create_time'),
        )
        sync_db.close()

if __name__ == '__main__':
    run_create()