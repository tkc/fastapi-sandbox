import json
import uuid

from app.core.logger import setup_logging


class TestTraceId:
    """trace_id がリクエスト処理中のログに常に含まれることを検証する。"""

    def test_response_has_trace_id_header(self, client):
        response = client.get("/users")
        assert "X-Trace-ID" in response.headers
        # UUID 形式であること
        uuid.UUID(response.headers["X-Trace-ID"])

    def test_custom_request_id_propagated(self, client):
        custom_id = "custom-trace-abc-123"
        response = client.get("/users", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Trace-ID"] == custom_id

    def test_trace_id_in_log_output(self, client, capfd):
        setup_logging(json_logs=True, log_level="INFO")
        response = client.get("/users")
        trace_id = response.headers["X-Trace-ID"]

        captured = capfd.readouterr()
        log_lines = [line for line in captured.err.strip().split("\n") if line.strip()]

        # アプリのログ行だけ抽出 (httpx 等の外部ログは除外)
        app_logs = []
        for line in log_lines:
            entry = json.loads(line)
            if entry.get("logger", "").startswith(("app.", "app/")):
                app_logs.append(entry)

        # アプリのログが出力されていること
        assert len(app_logs) > 0

        # 全てのアプリログ行に trace_id が含まれること
        for entry in app_logs:
            assert entry["trace_id"] == trace_id, f"trace_id missing or mismatched in log: {entry}"

    def test_each_request_gets_unique_trace_id(self, client):
        resp1 = client.get("/users")
        resp2 = client.get("/users")
        assert resp1.headers["X-Trace-ID"] != resp2.headers["X-Trace-ID"]
