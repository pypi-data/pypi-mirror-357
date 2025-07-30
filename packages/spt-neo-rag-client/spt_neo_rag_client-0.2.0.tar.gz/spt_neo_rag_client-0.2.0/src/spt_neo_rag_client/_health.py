"""Health check endpoints for the SPT Neo RAG Client."""

import asyncio
from typing import Dict, Any, TYPE_CHECKING

from .models import (
    HealthCheckResponse,
    DetailedHealthCheckResponse,
)

if TYPE_CHECKING:
    from .client import NeoRagClient


class HealthEndpoints:
    """Handles health check API operations."""

    def __init__(self, client: "NeoRagClient"):
        self._client = client

    async def get_health(self) -> HealthCheckResponse:
        """
        Perform a simple health check.
        
        Returns:
            HealthCheckResponse: Basic status information.
        """
        # Note: Needs authentication header even for basic health
        response = await self._client._request("GET", "/health")
        return HealthCheckResponse(**response.json())

    def get_health_sync(self) -> HealthCheckResponse:
        """Synchronous version of get_health."""
        return asyncio.run(self.get_health())

    async def get_detailed_health(self) -> DetailedHealthCheckResponse:
        """
        Perform a detailed health check including database connection.
        
        Returns:
            DetailedHealthCheckResponse: Detailed status of components.
        """
        response = await self._client._request("GET", "/health/detailed")
        return DetailedHealthCheckResponse(**response.json())

    def get_detailed_health_sync(self) -> DetailedHealthCheckResponse:
        """Synchronous version of get_detailed_health."""
        return asyncio.run(self.get_detailed_health()) 