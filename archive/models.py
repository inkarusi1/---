import datetime

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# Create your models here.
class BlockInfo(models.Model):
    block_id = models.AutoField(primary_key=True)
    block_name = models.CharField(max_length=128, default='undefined', unique=True)
    block_name_zh = models.CharField(max_length=128, default='未定义')
    block_function = models.TextField(default='none')
    lang = models.CharField(max_length=16, default='unselected')
    in_module = models.CharField(max_length=128, default='none')
    code = models.TextField(default='none')
    # block_file = models.CharField(max_length=64)
    # block_date = models.DateTimeField("date published")

    class Meta:
        db_table = 'block_info'
        ordering = ['block_id']
        verbose_name = 'BlockInfo'
        verbose_name_plural = 'BlockInfo'  # 模型的复数名称
        app_label = 'archive'  # 模型所属的应用程序标签

    def __str__(self):
        return self.block_name

    def clean(self) -> None:  # 重写clean方法，用于数据验证
        if self.block_name == self.block_name_zh:
            raise ValidationError('block_name and block_name_zh should not be the same')

    # def was_published_recently(self):
    #     return self.block_date >= timezone.now() - datetime.timedelta(days=1)


class CodeHierarchy(models.Model):
    # 外键是block_id，指向BlockInfo表的block_id，on_delete=models.CASCADE表示级联删除，db_column='block_id'表示数据库中的字段名
    # related_name='inferior_blocks'表示反向关联时使用inferior_blocks作为关联名，否则默认为codehierarchy_set
    block_id = models.ForeignKey(BlockInfo, on_delete=models.CASCADE, db_column='block_id',
                                 related_name='inferior_blocks')
    # null=True表示数据库中该字段可以为空，blank=True表示表单中该字段可以为空
    superior_block_id = models.ForeignKey(BlockInfo, on_delete=models.CASCADE,null=True,
                                          blank=True, db_column='superior_block_id', related_name='superior_blocks')
    # superior_block_id = models.ForeignKey('self', on_delete=models.CASCADE,
    #                                       null=True, blank=True, db_column='superior_block_id')
    is_leaf = models.BooleanField(default=True)

    class Meta:
        db_table = 'code_hierarchy'
        # ordering = ['code_id']
        app_label = 'archive'  # 模型所属的应用程序标签

    def __str__(self):
        return str(self.block_id)

    def clean(self) -> None:  # 重写clean方法，用于数据验证
        if self.block_id == self.superior_block_id:
            raise ValidationError('block_id and superior_block_id should not be the same')

    # def was_published_recently(self):
    #     return self.block_date >= timezone.now() - datetime.timedelta(days=1)
