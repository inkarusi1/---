from django.contrib import admin

# Register your models here.
from .models import BlockInfo, CodeHierarchy

admin.site.register(BlockInfo)
admin.site.register(CodeHierarchy)
