# PyConfBox Django Plugin

Django 애플리케이션에서 PyConfBox를 사용할 수 있게 해주는 플러그인입니다.

## 설치

```bash
pip install pyconfbox-django
```

## 사용법

### Django 설정에 미들웨어 추가

```python
# settings.py
MIDDLEWARE = [
    'pyconfbox_django.middleware.PyConfBoxMiddleware',
    # ... 다른 미들웨어들
]

# PyConfBox 설정
PYCONFBOX = {
    'default_storage': 'environment',
    'fallback_storage': 'memory',
    'env_prefix': 'DJANGO_',
}
```

### Django 저장소 사용

```python
from pyconfbox_django import DjangoStorage
from pyconfbox import Config

# Django 설정과 연동
django_storage = DjangoStorage()
config = Config(default_storage=django_storage)

# Django 설정에 자동 반영
config.set('DEBUG', True, scope='django')
config.set('SECRET_KEY', 'your-secret-key', scope='django')
```

## 라이선스

MIT License 