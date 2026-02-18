from app.container.container import DIContainer
from app.usecase.user.user_service import UserService


def get_user_service() -> UserService:
    """UserService の依存関数。

    エンドポイントで service: UserService = Depends(get_user_service) として使う。

    Depends() パターンの利点:
    - テスト時に app.dependency_overrides で簡単にモックへ差し替えられる
    - 関数シグネチャに依存が明示されるため、中身を読まなくても何が必要かわかる
    - FastAPI が依存のライフサイクル管理・キャッシュ・ネスト解決を担う
    - エンドポイントとコンテナの結合が薄くなり、DI 基盤の差し替えがこの関数だけで済む
    """
    return DIContainer.resolve(UserService)
