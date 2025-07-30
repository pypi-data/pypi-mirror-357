# PyConfBox PostgreSQL Plugin

PyConfBox용 PostgreSQL 데이터베이스 저장소 플러그인입니다.

## 설치

```bash
pip install pyconfbox-postgresql
```

## 사용법

```python
from pyconfbox_postgresql import PostgreSQLStorage
from pyconfbox import Config

# PostgreSQL 저장소 설정
postgresql_storage = PostgreSQLStorage(
    host='localhost',
    port=5432,
    user='postgres',
    password='password',
    database='config_db'
)

config = Config(default_storage=postgresql_storage)

# 설정 저장/조회
config.set('app_name', 'MyApp')
app_name = config.get('app_name')
```

## 라이선스

MIT License 