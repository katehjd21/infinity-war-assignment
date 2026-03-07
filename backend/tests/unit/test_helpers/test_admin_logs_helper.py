from datetime import datetime, timezone, timedelta
from models import RequestLog
from helpers.admin_logs import AdminLogsHelper


def test_get_recent_logs_returns_logs(create_admin_user):
    user = create_admin_user

    RequestLog.create(method="GET", path="/coins", user=user)
    RequestLog.create(method="POST", path="/login", user=None)

    logs = AdminLogsHelper.get_recent_logs()

    assert len(logs) == 2
    for log in logs:
        assert all(k in log for k in ["method", "path", "user", "timestamp"])
    assert any(log["user"] == "Anonymous" for log in logs)
    assert any(log["user"] == user.username for log in logs)


def test_get_recent_logs_orders_by_timestamp_desc(create_admin_user):
    user = create_admin_user

    older = datetime.now(timezone.utc) - timedelta(days=1)
    newer = datetime.now(timezone.utc)

    RequestLog.create(method="GET", path="/old", user=user, timestamp=older)
    RequestLog.create(method="GET", path="/new", user=user, timestamp=newer)

    logs = AdminLogsHelper.get_recent_logs()

    assert logs[0]["path"] == "/new"
    assert logs[1]["path"] == "/old"


def test_get_recent_logs_respects_limit(create_admin_user):
    user = create_admin_user

    for i in range(5):
        RequestLog.create(method="GET", path=f"/test{i}", user=user)

    logs = AdminLogsHelper.get_recent_logs(limit=3)
    assert len(logs) == 3

    expected_paths = ["/test4", "/test3", "/test2"]
    actual_paths = [log["path"] for log in logs]
    assert actual_paths == expected_paths


def test_get_recent_logs_timestamp_iso(create_admin_user):
    user = create_admin_user

    RequestLog.create(method="GET", path="/coins", user=user)

    logs = AdminLogsHelper.get_recent_logs()
    timestamp = logs[0]["timestamp"]

    assert isinstance(timestamp, str)
    assert "T" in timestamp
    assert len(timestamp.split("T")[1].split(":")) >= 3


def test_admin_logs_endpoint(logged_in_admin, create_admin_user):
    client = logged_in_admin
    user = create_admin_user

    RequestLog.create(method="GET", path="/coins", user=user)
    RequestLog.create(method="POST", path="/login", user=None)

    response = client.get("/admin/logs")
    assert response.status_code == 200

    logs = response.get_json()
    assert isinstance(logs, list)
    for log in logs:
        assert all(k in log for k in ["method", "path", "user", "timestamp"])

    timestamps = [log["timestamp"] for log in logs]
    assert timestamps == sorted(timestamps, reverse=True)