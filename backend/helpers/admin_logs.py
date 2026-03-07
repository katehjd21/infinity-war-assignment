from datetime import datetime
from models import RequestLog

class AdminLogsHelper:

    @staticmethod
    def get_recent_logs(limit=100):
        logs = (
            RequestLog
            .select()
            .order_by(RequestLog.timestamp.desc())
            .limit(limit)
        )

        return [
            {
                "method": log.method,
                "path": log.path,
                "user": log.user.username if log.user else "Anonymous",
                "timestamp": (
                    log.timestamp.isoformat() 
                    if isinstance(log.timestamp, datetime) 
                    else datetime.fromisoformat(str(log.timestamp)).isoformat()
                )
            }
            for log in logs
        ]