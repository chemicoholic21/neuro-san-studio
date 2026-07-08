# Copyright © 2025-2026
#
# CodedTool adapter: exposes the deterministic laptop-spec queries to the
# agent network. All facts come from laptop_data (local CSV) — never from
# the model. The agent MUST call this tool to talk about specs or price.

import asyncio
import logging
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool

from coded_tools.laptop_advisor import laptop_data

logger = logging.getLogger(__name__)


class LaptopSpecsTool(CodedTool):
    """Filter the laptop catalog or look up one laptop's specs from local data."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        logger.info("********** LaptopSpecsTool started **********")

        # Single-laptop lookup takes precedence when an id/name is supplied.
        identifier = args.get("id_or_name")
        if identifier:
            laptop = laptop_data.get_laptop(identifier)
            if laptop is None:
                return {"error": f"No laptop found matching '{identifier}'.", "matches": []}
            return {"query": args, "matches": [laptop], "count": 1}

        matches = laptop_data.filter_laptops(
            max_price=args.get("max_price"),
            min_ram_gb=args.get("min_ram_gb"),
            use_case=args.get("use_case"),
            max_weight_kg=args.get("max_weight_kg"),
            os_name=args.get("os_name"),
            brand=args.get("brand"),
        )
        logger.info("LaptopSpecsTool matched %d laptops", len(matches))
        return {"query": args, "matches": matches, "count": len(matches)}

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return await asyncio.to_thread(self.invoke, args, sly_data)
