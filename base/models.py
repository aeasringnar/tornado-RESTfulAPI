from base.settings import async_db, sync_db
from peewee import Model, DateTimeField, ModelSelect, Node
from datetime import datetime

class BaseModel(Model):
    create_time = DateTimeField(default=datetime.now, verbose_name="添加时间", help_text='添加时间')
    update_time = DateTimeField(default=datetime.now, verbose_name='更新时间', help_text='更新时间')

    def save(self, *args, **kwargs):
        if self._get_pk_value() is None:
            self.create_time = datetime.now()
        self.update_time = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)
    
    def update(self, *args, **kwargs):
        self.update_time = datetime.now()
        return super(BaseModel, self).update(*args, **kwargs)

    class Meta:
        database = sync_db