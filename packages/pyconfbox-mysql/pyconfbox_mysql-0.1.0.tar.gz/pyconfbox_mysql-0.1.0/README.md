# PyConfBox MySQL Plugin

PyConfBox용 MySQL 데이터베이스 저장소 플러그인입니다.

## 설치

```bash
pip install pyconfbox-mysql
```

## 사용법

```python
from pyconfbox_mysql import MySQLStorage
from pyconfbox import Config

# MySQL 저장소 설정
mysql_storage = MySQLStorage(
    host='localhost',
    port=3306,
    user='root',
    password='password',
    database='config_db'
)

config = Config(default_storage=mysql_storage)

# 설정 저장/조회
config.set('app_name', 'MyApp')
app_name = config.get('app_name')
```

## 라이선스

MIT License 