#!/usr/bin/env python3
"""Entry point for Claude Monitor - redirects to the refactored package."""

# from src.usage_analyzer import api
#
# if __name__ == "__main__":
#     api.analyze_usage()
import sentry_sdk

from src.claude_monitor import main

sentry_sdk.init(
    dsn="https://1c7819039fc64a24b32e94abbc4a1f86@o4509550623326208.ingest.de.sentry.io/4509550625620048",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    traces_sample_rate=1.0,
)
if __name__ == "__main__":
    from src.claude_monitor.utils.auto_upgrade import auto_upgrade_check
    auto_upgrade_check()
    main()
