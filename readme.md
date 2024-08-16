# 后端测试版本

## Python 环境

python 版本：3.9.18

```bash
# pip安装环境依赖，需要3.9.18的python虚拟环境
pip install -r requirements.txt

# conda新建环境，需要修改environment.yml的首行和末行的参数
conda env create -f environment.yml
conda activate django_env
```



## 数据库准备

安装 MySQL 后，新建数据库 `code_db`；

在项目的 `./gencode/settings.py` 的 `DATABASES` 部分修改自己的 `USER` 和 `PASSWORD`；

运行如下命令进行数据库迁移：

```bash
py manage.py makemigrations
py manage.py migrate
```



## 运行测试

```bash
py manage.py runserver
```

之后访问 http://127.0.0.1:8000/archive/ 即可进入测试页面