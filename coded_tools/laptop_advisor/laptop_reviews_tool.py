# Copyright © 2025-2026
#
# CodedTool adapter: exposes review/reliability facts from the local dataset.

import asyncio
import logging
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool

from coded_tools.laptop_advisor import laptop_data

logger = logging.getLogger(__name__)


class LaptopReviewsTool(CodedTool):
    """Return the review record (rating, reliability, pros/cons) for a laptop."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        logger.info("********** LaptopReviewsTool started **********")
        identifier = args.get("id_or_name")
        if not identifier:
            return {"error": "id_or_name is required."}
        review = laptop_data.get_reviews(identifier)
        if review is None:
            return {"error": f"No reviews found for '{identifier}'."}
        return review

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return await asyncio.to_thread(self.invoke, args, sly_data)
