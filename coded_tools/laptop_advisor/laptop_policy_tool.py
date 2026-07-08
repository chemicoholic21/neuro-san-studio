# Copyright © 2025-2026
#
# CodedTool adapter: exposes brand warranty/return/support policy facts.

import asyncio
import logging
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool

from coded_tools.laptop_advisor import laptop_data

logger = logging.getLogger(__name__)


class LaptopPolicyTool(CodedTool):
    """Return warranty, return-window and support facts for a laptop brand."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        logger.info("********** LaptopPolicyTool started **********")
        brand = args.get("brand")
        if not brand:
            return {"error": "brand is required."}
        policy = laptop_data.get_policy(brand)
        if policy is None:
            return {"error": f"No policy on file for brand '{brand}'."}
        return policy

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return await asyncio.to_thread(self.invoke, args, sly_data)
