# fastapi-sandbox

FastAPI + DynamoDB で構築した User API のサンドボックスプロジェクト。
クリーンアーキテクチャの実践と、構造化ログ・型安全性・定数管理などの横断的関心事を検証する。

## Tech Stack

| Category | Tool |
|---|---|
| Web Framework | FastAPI |
| Database | Amazon DynamoDB (Local) |
| DI Container | injector |
| Logging | structlog |
| Validation | Pydantic / pydantic-settings |
| Linter / Formatter | Ruff |
| Type Checker | ty |
| Test | pytest |
| Runtime | Python 3.13, uv |

## Libraries

### FastAPI

ASGI ベースの Web フレームワーク。`Depends()` による DI、Pydantic モデルによるリクエスト/レスポンスの自動バリデーション、`exception_handler` によるグローバル例外処理を活用。Starlette の `BaseHTTPMiddleware` を継承したログミドルウェアもここに乗る。

### boto3

AWS SDK for Python。DynamoDB テーブルの CRUD 操作に `dynamodb.Table` リソース API を使用。ローカル開発では DynamoDB Local (`localhost:8000`) に接続する。

### injector

Python の DI コンテナライブラリ。`IUserRepository` インターフェースを `UserDynamoDBRepository` にバインドし、`UserService` のコンストラクタへ自動注入する。バインディング定義は `app/container/container.py` に集約。

### Pydantic / pydantic-settings

- **Pydantic**: ドメインエンティティ (`User`) と API スキーマ (`UserCreate`, `UserResponse`) の定義に使用。`Field` による入力バリデーション（文字列長、数値範囲）、`EmailStr` によるメールアドレス検証を提供。
- **pydantic-settings**: 環境変数ベースのアプリ設定 (`Settings`) を管理。DynamoDB 接続先やログレベルを外部から注入可能にする。

### structlog

構造化ログライブラリ。stdlib logging と統合し、JSON / コンソール出力を切替可能。`contextvars` を利用してリクエストスコープの `trace_id` を全ログ行に自動付与する。`@log_action()` デコレータと組み合わせ、メソッド単位の開始・成功・エラーログを自動記録。

### Ruff

Linter と Formatter を兼ねるツール。`pycodestyle`, `pyflakes`, `isort`, `flake8-bugbear`, `pyupgrade`, `flake8-annotations` 相当のルールを有効化。テストコードでは `ANN` (型アノテーション) ルールを除外。

### ty

Python の型チェッカー。`app/` 配下のコードに対して静的型検査を実施し、`NewType` (`UserId`) の誤用を検出する。

### pytest

テストフレームワーク。単体テスト（usecase, domain, core, infrastructure）と結合テスト（API エンドポイント, ログ検証）の2レベルで構成。`MagicMock(spec=...)` によるリポジトリのモック、`structlog.testing.capture_logs()` によるログ出力の検証を行う。

## Architecture

クリーンアーキテクチャに基づき、依存の方向を **外側 → 内側** に統一している。

```
┌─────────────────────────────────────────────────────┐
│  API Layer (app/api/)                               │
│  FastAPI endpoints, dependency injection             │
├─────────────────────────────────────────────────────┤
│  Usecase Layer (app/usecase/)                       │
│  Application business logic (UserService)            │
├─────────────────────────────────────────────────────┤
│  Domain Layer (app/domain/)                         │
│  Entities, repository interfaces                     │
├─────────────────────────────────────────────────────┤
│  Infrastructure Layer (app/infrastructure/)          │
│  DynamoDB repository implementation, datasource      │
└─────────────────────────────────────────────────────┘
```

### 依存関係

```
API → Usecase → Domain ← Infrastructure
```

- **Domain** は他のどの層にも依存しない（純粋なエンティティとインターフェース）
- **Infrastructure** は Domain のインターフェース (`IUserRepository`) を実装する（依存性逆転）
- **Usecase** は Domain のインターフェースにのみ依存し、具体実装を知らない
- **API** は Usecase を呼び出すだけの薄いレイヤー

### ディレクトリ構成

```
app/
├── api/                          # API Layer
│   ├── dependencies.py           #   FastAPI Depends() でサービスを解決
│   └── v1/endpoints/users.py     #   REST エンドポイント定義
├── usecase/                      # Usecase Layer
│   └── user/user_service.py      #   ビジネスロジック (CRUD + 検索)
├── domain/                       # Domain Layer
│   └── user/
│       ├── entity.py             #   User エンティティ (Pydantic BaseModel)
│       └── i_user_repository.py  #   リポジトリインターフェース (ABC)
├── infrastructure/               # Infrastructure Layer
│   ├── datasource/dynamodb.py    #   DynamoDB リソース/テーブル生成
│   ├── repository/               #   IUserRepository の DynamoDB 実装
│   └── constants.py              #   DynamoDB 固有の定数
├── core/                         # Cross-cutting concerns
│   ├── types.py                  #   NewType 定義 (UserId)
│   ├── constants.py              #   アプリ共通定数
│   ├── config.py                 #   pydantic-settings による設定管理
│   ├── decorators.py             #   @log_action 構造化ログデコレータ
│   ├── exceptions.py             #   例外階層 (AppError → UserNotFoundError, RepositoryError)
│   ├── exception_handlers.py     #   FastAPI グローバル例外ハンドラー
│   └── logger.py                 #   structlog セットアップ
├── container/                    # DI Container
│   └── container.py              #   injector によるバインディング定義
├── middleware/                   # Middleware
│   └── logging_middleware.py     #   リクエスト単位の trace_id 付与・ログ出力
├── schemas/                      # API Schemas
│   └── user.py                   #   リクエスト/レスポンス用 Pydantic モデル
└── main.py                       # アプリケーションエントリーポイント
```

### 横断的関心事

#### 型安全性

`typing.NewType` で `UserId` 型を定義し、全層で `user_id: str` の代わりに `user_id: UserId` を使用。
素の `str` との混同を型チェッカーレベルで防止する。

#### 構造化ログ

- **リクエストレベル**: `LoggingMiddleware` が `X-Request-ID` ヘッダーから `trace_id` を取得し、structlog の contextvars にバインド。全ログ行にリクエスト単位のトレースIDが自動付与される。
- **メソッドレベル**: `@log_action()` デコレータが開始・成功・エラーの3イベントを自動記録。引数のサニタイズ（`exclude_args` でリダクション）、実行時間の計測を含む。

#### 例外ハンドリング

詳細は後述の [Error Design](#error-design) を参照。

#### 定数管理

文字列・数値リテラルを `app/core/constants.py`（アプリ共通）と `app/infrastructure/constants.py`（DynamoDB 固有）に集約。変更時の影響範囲を明確化。

## Error Design

### 例外階層

```
Exception
 └── AppError                    # アプリケーション基底例外 (message: str)
      ├── UserNotFoundError      # ユーザー未検出 (user_id: UserId)
      └── RepositoryError        # データアクセス失敗 (operation: str)
```

- **`AppError`** — 全てのアプリケーション例外の基底クラス。`message` 属性を持つ。
- **`UserNotFoundError`** — リポジトリが `None` を返した場合に Usecase 層で送出。`user_id` を保持し、ログとレスポンスに含める。
- **`RepositoryError`** — boto3 の `ClientError` / `BotoCoreError` を Infrastructure 層でキャッチし、`from err` で原因チェーンを保持したまま送出。`operation` 属性で失敗した操作名 (`save`, `find_by_id` 等) を記録する。

### 例外の発生箇所と伝播

```
Infrastructure Layer                    Usecase Layer
──────────────────                      ─────────────
boto3 ClientError                       repo.find_by_id() == None
      │                                        │
      ▼                                        ▼
RepositoryError (from err)              UserNotFoundError(user_id)
      │                                        │
      └──────────────┐  ┌─────────────────────┘
                     ▼  ▼
              FastAPI exception_handler
              (app/core/exception_handlers.py)
```

- エンドポイントは `try/except` を持たない。全ての例外はグローバルハンドラーで処理される。
- Infrastructure 層は boto3 例外を `RepositoryError` にラップし、内部実装の詳細を上位層に漏らさない。

### HTTP レスポンスマッピング

| Exception | Status Code | Response Body | Log Level |
|---|---|---|---|
| `UserNotFoundError` | `404 Not Found` | `{"detail": "User not found"}` | `WARNING` |
| `RepositoryError` | `500 Internal Server Error` | `{"detail": "Internal server error"}` | `ERROR` |
| `AppError` | `500 Internal Server Error` | `{"detail": "Internal server error"}` | `ERROR` |

- クライアントに内部エラーの詳細（スタックトレース、DB エラーメッセージ）は返さない。
- 全てのハンドラーは構造化ログに `user_id`, `operation`, `message`, `path` 等のコンテキストを出力する。
- HTTP ステータスコードは `starlette.status` の定数を使用。

### ログイベント

例外ハンドラーが出力するログイベント名は `app/core/constants.py` で一元管理される。

| Constant | Event Name | Trigger |
|---|---|---|
| `LOG_USER_NOT_FOUND` | `user_not_found` | `UserNotFoundError` 捕捉時 |
| `LOG_REPOSITORY_ERROR` | `repository_error` | `RepositoryError` 捕捉時 |
| `LOG_APP_ERROR` | `app_error` | `AppError` 捕捉時 |

### バリデーションエラー

リクエストボディのバリデーションは Pydantic / FastAPI が自動処理する。

| Validation | Rule | Response |
|---|---|---|
| `name` | 1〜100文字 | `422 Unprocessable Entity` |
| `email` | RFC 5322 準拠 | `422 Unprocessable Entity` |
| `age` | 0〜150 | `422 Unprocessable Entity` |
| `address` | 1〜500文字 | `422 Unprocessable Entity` |

これらは FastAPI のデフォルトハンドラーが処理し、フィールド単位のエラー詳細を JSON で返却する。

## Setup

```bash
# 依存インストール
uv sync

# DynamoDB Local 起動
docker run -d -p 8000:8000 amazon/dynamodb-local

# サーバー起動
uv run uvicorn app.main:app --reload
```

## Development

```bash
# テスト
uv run pytest tests/ -v

# Lint & Format
uv run ruff format app/ tests/
uv run ruff check . --fix

# 型チェック
uv run ty check app/
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/users` | ユーザー作成 |
| `GET` | `/users` | ユーザー一覧取得 |
| `GET` | `/users/search?name=&email=` | ユーザー検索 |
| `GET` | `/users/{user_id}` | ユーザー取得 |
| `GET` | `/health` | ヘルスチェック |
