from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# 동작 흐름:
# 1. models.py에서 Base를 import하여 프로젝트의 모든 모델 정보를 가져옵니다.
# 2. Base.metadata를 target_metadata에 할당합니다.
# 3. Alembic이 이 메타데이터를 사용하여 현재 모델 상태와 데이터베이스 스키마를 비교합니다.
# 4. 'alembic revision --autogenerate' 명령 실행 시 모델 변경사항을 자동으로 감지하여
#    마이그레이션 스크립트를 생성합니다.
from models import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    오프라인 모드에서 마이그레이션 실행
    
    동작 흐름:
    1. 데이터베이스에 직접 연결하지 않고 마이그레이션 스크립트만 생성
    2. alembic.ini에서 데이터베이스 URL을 읽어옴
    3. target_metadata(모델 정보)와 URL을 사용하여 마이그레이션 컨텍스트 설정
    4. 마이그레이션 스크립트를 실행하여 SQL 문을 생성
    
    사용 시나리오:
    - 데이터베이스 서버에 직접 접근할 수 없는 경우
    - 마이그레이션 스크립트를 먼저 검토하고 싶은 경우
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    온라인 모드에서 마이그레이션 실행
    
    동작 흐름:
    1. alembic.ini 설정을 읽어서 데이터베이스 엔진 생성
    2. 데이터베이스에 실제 연결을 생성
    3. 연결과 모델 메타데이터를 사용하여 마이그레이션 컨텍스트 설정
    4. 트랜잭션 내에서 마이그레이션 실행 (실제 데이터베이스 스키마 변경)
    
    사용 시나리오:
    - 일반적인 마이그레이션 실행 (alembic upgrade head)
    - 데이터베이스에 직접 접근하여 스키마를 변경하는 경우
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# 동작 흐름:
# Alembic이 실행 모드를 자동으로 감지하여 적절한 함수를 호출합니다.
# - 오프라인 모드: 'alembic upgrade --sql' 같은 명령 실행 시
# - 온라인 모드: 'alembic upgrade head' 같은 일반적인 마이그레이션 실행 시
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
