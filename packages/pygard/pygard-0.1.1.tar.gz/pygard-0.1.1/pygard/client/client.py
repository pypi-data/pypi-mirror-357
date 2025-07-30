# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:07
# @Description:


"""
Main client class for PyGard.
"""

from typing import Optional

from ..config import GardConfig
from ..core import setup_logger, ConnectionManager
from ..services import GardService
from ..models import Gard, GardFilter, GardPage


class GardClient:
    """
    Main client for interacting with the Gard data service.
    
    This client provides a high-level interface for all Gard operations,
    including connection management, logging, and service access.
    """

    def __init__(
            self,
            config: Optional[GardConfig] = None,
            **kwargs
    ) -> None:
        """
        Initialize Gard client.
        
        Args:
            config: Gard configuration (optional)
            **kwargs: Configuration overrides
        """
        # Initialize configuration
        if config is None:
            config = GardConfig()

        # Apply any overrides
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.config = config

        # Setup logging
        self.logger = setup_logger(
            level=config.log_level,
            format_type=config.log_format
        )

        # Initialize connection manager
        self._connection_manager = ConnectionManager(config)

        # Initialize services
        self._gard_service = GardService(self._connection_manager, config)

        self.logger.info(
            "Gard client initialized",
            base_url=config.base_url,
            api_version=config.api_version
        )

    async def __aenter__(self) -> "GardClient":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the client and establish connections."""
        await self._connection_manager.start()
        self.logger.info("Gard client started")

    async def close(self) -> None:
        """Close the client and clean up resources."""
        await self._connection_manager.close()
        self.logger.info("Gard client closed")

    @property
    def gard(self) -> GardService:
        """Get the Gard service."""
        return self._gard_service

    # Convenience methods for common operations
    async def create_gard(self, gard: Gard) -> Gard:
        """Create a new Gard record."""
        return await self.gard.create_gard(gard)

    async def get_gard(self, did: int) -> Gard:
        """Get a Gard record by ID."""
        return await self.gard.get_gard(did)

    async def update_gard(self, did: int, gard: Gard) -> Gard:
        """Update a Gard record."""
        return await self.gard.update_gard(did, gard)

    async def delete_gard(self, did: int) -> bool:
        """Delete a Gard record."""
        return await self.gard.delete_gard(did)

    async def list_gards(self, page: int = 1, size: int = 10) -> GardPage:
        """List Gard records with pagination."""
        return await self.gard.list_gards(page, size)

    async def search_gards(
            self,
            filter_obj: GardFilter,
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """Search Gard records with filters."""
        return await self.gard.search_gards(filter_obj, page, size)

    async def search_by_tags(
            self,
            tags: list[str],
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """Search Gard records by tags."""
        return await self.gard.search_by_tags(tags, page, size)

    async def search_by_keywords(
            self,
            keywords: list[str],
            page: int = 1,
            size: int = 10
    ) -> GardPage:
        """Search Gard records by keywords."""
        return await self.gard.search_by_keywords(keywords, page, size)

    async def get_all_gards(self) -> list[Gard]:
        """Get all Gard records."""
        return await self.gard.get_all_gards()

    def get_connection_info(self) -> dict:
        """Get connection information."""
        return {
            "base_url": self.config.base_url,
            "api_version": self.config.api_version,
            "timeout": self.config.timeout,
            "connection_pool_size": self.config.connection_pool_size,
        }
