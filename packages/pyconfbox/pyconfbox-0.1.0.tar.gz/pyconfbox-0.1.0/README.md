# PyConfBox 🎯

**Python Configuration Management with Multiple Storage Backends**

PyConfBox는 환경변수, 시스템변수, 글로벌변수 등 모든 설정을 통합 관리할 수 있는 강력한 Python 설정 관리 라이브러리입니다.

## ✨ 주요 기능

- **🏗️ 다양한 저장소 지원**: Memory, Environment, File (JSON/YAML/TOML), SQLite, Redis
- **🎯 범위(Scope) 시스템**: env, global, local, system, secret, django 범위 지원
- **🔒 불변성(Immutability) 제어**: 설정별 불변 지정 및 전체 릴리즈 모드
- **🔄 자동 타입 변환**: 문자열 → int, float, bool, list, dict 자동 변환
- **🔌 플러그인 아키텍처**: 확장 가능한 저장소 및 플러그인 시스템
- **📊 메타데이터 관리**: 설정 통계 및 상태 추적

## 🚀 빠른 시작

### 설치

```bash
pip install pyconfbox
```

### 기본 사용법

```python
from pyconfbox import Config, ConfigScope

# Config 인스턴스 생성
config = Config(default_storage="memory", fallback_storage="environment")

# 기본 설정
config.set("app_name", "MyApp")
config.set("debug", True)

# 타입 변환
config.set("port", "8080", data_type=int)
config.set("timeout", "30.5", data_type=float)
config.set("hosts", "localhost,127.0.0.1", data_type=list)

# 범위별 설정
config.set("database_url", "sqlite:///app.db", scope=ConfigScope.LOCAL)
config.set("secret_key", "super-secret", scope=ConfigScope.SECRET, immutable=True)

# 설정 조회
app_name = config.get("app_name")
port = config.get("port")  # 자동으로 int 타입
hosts = config.get("hosts")  # 자동으로 list 타입

# 범위별 조회
global_configs = config.get_by_scope(ConfigScope.GLOBAL)
secret_configs = config.get_by_scope(ConfigScope.SECRET)

# 릴리즈 모드 (모든 설정 고정)
config.release()
```

### 파일 저장소 사용

```python
from pyconfbox import Config, JSONStorage, YAMLStorage, TOMLStorage

# JSON 파일 저장소
json_storage = JSONStorage('config.json')
config = Config(default_storage=json_storage)

config.set('app_name', 'MyApp')
config.set('version', '1.0.0')
config.set('features', ['auth', 'cache', 'logging'])

# YAML 파일 저장소
yaml_storage = YAMLStorage('config.yaml')
config = Config(default_storage=yaml_storage)

config.set('database', {
    'host': 'localhost',
    'port': 5432,
    'name': 'myapp_db'
})

# TOML 파일 저장소 
toml_storage = TOMLStorage('config.toml')
config = Config(default_storage=toml_storage)

config.set('owner', {
    'name': 'John Doe',
    'email': 'john@example.com'
})
```

### SQLite 저장소 사용

```python
from pyconfbox import Config, SQLiteStorage

# 인메모리 SQLite
memory_storage = SQLiteStorage()  # ":memory:"
config = Config(default_storage=memory_storage)

# 파일 SQLite
file_storage = SQLiteStorage('config.db')
config = Config(default_storage=file_storage)

config.set('session_timeout', 3600)
config.set('max_connections', 100)

# 배치 업데이트
batch_data = {
    'env': 'production',
    'region': 'us-west-2',
    'replicas': 3
}
file_storage.update(batch_data)
```

## 📋 설정 범위(Scope)

| 범위 | 설명 | 사용 예시 |
|------|------|-----------|
| `env` | 환경변수 | OS 환경변수, 프로세스별 설정 |
| `global` | 글로벌변수 | 애플리케이션 전역 설정 |
| `local` | 로컬변수 | 모듈/클래스별 지역 설정 |
| `system` | 시스템변수 | 시스템 레벨 설정 |
| `secret` | 비밀변수 | 암호화가 필요한 민감한 설정 |
| `django` | Django설정 | Django 전용 설정 |

## 🏗️ 저장소 아키텍처

### 내장 저장소
- **Memory**: 인메모리 저장소 (기본)
- **Environment**: 환경변수 저장소 (읽기 전용)
- **File**: 파일 기반 저장소 (JSON, YAML, TOML)
- **Redis**: Redis 저장소
- **SQLite**: SQLite 데이터베이스 저장소

### 플러그인 저장소 (별도 패키지)
- **pyconfbox-mysql**: MySQL 저장소
- **pyconfbox-postgresql**: PostgreSQL 저장소
- **pyconfbox-mongodb**: MongoDB 저장소
- **pyconfbox-django**: Django 통합 플러그인

## 🔒 불변성 관리

```python
# 개별 설정 불변 지정
config.set("api_key", "secret", immutable=True)

# 불변 설정 변경 시도 (예외 발생)
try:
    config.set("api_key", "new_secret")
except ImmutableConfigError:
    print("불변 설정은 변경할 수 없습니다!")

# 전체 설정 고정 (릴리즈 모드)
config.release()

# 릴리즈 후 설정 변경 시도 (예외 발생)
try:
    config.set("new_key", "value")
except ReleasedConfigError:
    print("릴리즈된 설정은 변경할 수 없습니다!")
```

## 🔄 자동 타입 변환

```python
# 문자열 → 정수
config.set("port", "8080", data_type=int)
assert config.get("port") == 8080

# 문자열 → 불린
config.set("debug", "true", data_type=bool)
assert config.get("debug") is True

# 문자열 → 리스트 (콤마 구분)
config.set("hosts", "localhost,127.0.0.1", data_type=list)
assert config.get("hosts") == ["localhost", "127.0.0.1"]

# 문자열 → 딕셔너리 (JSON)
config.set("db_config", '{"host": "localhost", "port": 5432}', data_type=dict)
assert config.get("db_config") == {"host": "localhost", "port": 5432}
```

## 📊 메타데이터 및 통계

```python
metadata = config.get_metadata()

print(f"총 설정 개수: {metadata.total_configs}")
print(f"범위별 개수: {metadata.scopes}")
print(f"저장소별 개수: {metadata.storages}")
print(f"불변 설정 개수: {metadata.immutable_count}")
print(f"릴리즈 여부: {metadata.is_released}")
```

## 🔌 고급 사용법

### 환경변수 접두어 사용

```python
config = Config(
    default_storage="environment",
    env_prefix="MYAPP_"
)

# MYAPP_DEBUG 환경변수 조회
debug = config.get("DEBUG")
```

### 다중 저장소 폴백

```python
config = Config(
    default_storage="redis",
    fallback_storage="memory"
)

# Redis에서 먼저 찾고, 없으면 메모리에서 찾기
value = config.get("key", default="default_value")
```

### 저장소별 설정 지정

```python
# 특정 저장소에 저장
config.set("cache_key", "value", storage="redis")
config.set("temp_data", "value", storage="memory")
```

## 🧪 테스트

```bash
# 개발 환경 설정
uv sync --dev

# 테스트 실행
uv run pytest

# 커버리지와 함께 테스트
uv run pytest --cov=pyconfbox

# 특정 테스트 실행
uv run pytest tests/test_config.py -v
```

## 📚 문서

- [API 레퍼런스](docs/api/)
- [사용 가이드](docs/guides/)
- [예제 코드](docs/examples/)

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🔗 관련 링크

- [GitHub Repository](https://github.com/dan1901/pyconfbox)
- [PyPI Package](https://pypi.org/project/pyconfbox/)
- [Documentation](https://github.com/dan1901/pyconfbox/tree/main/docs)
- [Issues](https://github.com/dan1901/pyconfbox/issues)

---

**Made with ❤️ by PyConfBox Team**
