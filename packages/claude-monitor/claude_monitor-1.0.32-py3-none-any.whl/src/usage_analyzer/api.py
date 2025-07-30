"""
Simplified main entry point for Claude Usage Analyzer.

This module provides a streamlined interface to generate response_final.json
with only the essential functionality needed.
"""

import json

from src.usage_analyzer.core.calculator import BurnRateCalculator
from src.usage_analyzer.core.data_loader import DataLoader
from src.usage_analyzer.core.identifier import SessionBlockIdentifier
from src.usage_analyzer.models.data_structures import CostMode
from src.usage_analyzer.output.json_formatter import JSONFormatter
from src.usage_analyzer.uploader import UsageUploader


def analyze_usage(plan: str = "pro", timezone: str = "Europe/Warsaw"):
    """Main entry point to generate response_final.json.

    Args:
        plan: Claude plan type (pro, max5, max20, custom_max)
        timezone: Timezone string for the user
    """

    data_loader = DataLoader()
    identifier = SessionBlockIdentifier(session_duration_hours=5)
    calculator = BurnRateCalculator()
    formatter = JSONFormatter()
    uploader = UsageUploader(plan=plan, timezone=timezone)

    # Load usage data from Claude directories (using AUTO mode by default)
    # print("Loading usage data...")
    entries, limit_messages = data_loader.load_usage_data(mode=CostMode.AUTO)
    # print(f"Loaded {len(entries)} usage entries and {len(limit_messages)} limit messages")

    # Identify session blocks
    # print("Identifying session blocks...")
    blocks = identifier.identify_blocks(entries, limit_messages)

    for block in blocks:
        if block.is_active:
            burn_rate = calculator.calculate_burn_rate(block)
            if burn_rate:
                block.burn_rate_snapshot = burn_rate
                projection = calculator.project_block_usage(block)
                if projection:
                    block.projection_data = {
                        "totalTokens": projection.projected_total_tokens,
                        "totalCost": projection.projected_total_cost,
                        "remainingMinutes": projection.remaining_minutes,
                    }

    json_output = formatter.format_blocks(blocks)
    result = json.loads(json_output)

    filtered = process_filter(result, uploader)
    #
    # result['avg_tokens'] = filtered.get('avg', 0)
    # result['max_tokens'] = filtered.get('max', 0)
    # # print(filtered)


    return result


def process_filter(result, uploader):
    # Filter to return only requested fields
    filtered_blocks = []
    for block in result["blocks"]:
        # Filter perModelStats to exclude 'unknown' and '<synthetic>' models
        filtered_per_model_stats = {
            model: stats
            for model, stats in block["perModelStats"].items()
            if model not in ["unknown", "<synthetic>"]
        }

        filtered_block = {
            "startTime": block["startTime"],
            "endTime": block["endTime"],
            "actualEndTime": block["actualEndTime"],
            "perModelStats": filtered_per_model_stats,
            "totalTokens": block["totalTokens"],
            "totalTokensOld": block["totalTokensOld"],
            "costUSD": block["costUSD"],
            "entries": block["entries"],
            "limits": block["limits"],
        }
        filtered_blocks.append(filtered_block)



    blocks_with_general_limit=[]
    results_tokens=[]
    for block1 in filtered_blocks:
        if block1['limits']:  # Check if limits is not empty
            # Check if any limit has type 'general_limit'
            has_general_limit = any(limit['type'] == 'general_limit' for limit in block1['limits'])
            if has_general_limit:
                results_tokens.append(block1["totalTokens"])
            blocks_with_general_limit.append(block1)

    if blocks_with_general_limit:
        upload_data = {"blocks": filtered_blocks}
        uploader.upload_usage_data(upload_data)

    if len(results_tokens) > 2:
        return {
            "max": max(results_tokens),
            "avg": sum(results_tokens) / len(results_tokens)
        }
