# PyConfBox MongoDB Plugin

PyConfBox용 MongoDB 문서 데이터베이스 저장소 플러그인입니다.

## 설치

```bash
pip install pyconfbox-mongodb
```

## 사용법

```python
from pyconfbox_mongodb import MongoDBStorage
from pyconfbox import Config

# MongoDB 저장소 설정
mongodb_storage = MongoDBStorage(
    host='localhost',
    port=27017,
    database='config_db',
    collection='configurations'
)

config = Config(default_storage=mongodb_storage)

# 설정 저장/조회
config.set('app_name', 'MyApp')
app_name = config.get('app_name')
```

## 라이선스

MIT License 