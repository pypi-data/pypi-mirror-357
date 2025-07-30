"""Admin endpoints for the SPT Neo RAG Client."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from uuid import UUID

from .models import (
    SystemStatisticsResponse,
    TokenUsageResponse,
    MaintenanceResponse,
    AuditRecordResponse,
    AuditCheckResponse,
    AuditCleanupResponse,
    LicenseStatusResponse,
)

if TYPE_CHECKING:
    from .client import NeoRagClient


class AdminEndpoints:
    """Handles admin-related API operations."""

    def __init__(self, client: "NeoRagClient"):
        self._client = client

    async def get_health_check(self) -> Dict[str, Any]:
        """
        Perform a system health check (admin only).
        
        Returns:
            Dict[str, Any]: Detailed health information.
        """
        response = await self._client._request("GET", "/admin/health")
        return response.json()

    def get_health_check_sync(self) -> Dict[str, Any]:
        """Synchronous version of get_health_check."""
        return asyncio.run(self.get_health_check())

    async def get_system_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get system statistics for the specified number of days (admin only).
        
        Args:
            days: Number of days of statistics to retrieve (default: 7).
            
        Returns:
            Dict[str, Any]: System statistics data.
        """
        params = {"days": days}
        response = await self._client._request("GET", "/admin/stats", params=params)
        return response.json()

    def get_system_statistics_sync(self, days: int = 7) -> Dict[str, Any]:
        """Synchronous version of get_system_statistics."""
        return asyncio.run(self.get_system_statistics(days=days))

    async def get_token_usage(
        self,
        period: str = "day",
        model: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> TokenUsageResponse:
        """
        Get token usage statistics (admin only).
        
        Args:
            period: Period to aggregate by (day, week, month, year).
            model: Filter by specific model.
            start_date: Start date for custom range.
            end_date: End date for custom range.
            
        Returns:
            TokenUsageResponse: Token usage data.
        """
        params = {"period": period}
        if model:
            params["model"] = model
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
            
        response = await self._client._request("GET", "/admin/token-usage", params=params)
        return TokenUsageResponse(**response.json())

    def get_token_usage_sync(
        self,
        period: str = "day",
        model: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> TokenUsageResponse:
        """Synchronous version of get_token_usage."""
        return asyncio.run(self.get_token_usage(period, model, start_date, end_date))

    async def optimize_vector_indexes(self) -> MaintenanceResponse:
        """
        Trigger background task to optimize vector indexes (admin only).
        
        Returns:
            MaintenanceResponse: Task status information.
        """
        response = await self._client._request("POST", "/admin/maintenance/optimize-vectors")
        return MaintenanceResponse(**response.json())

    def optimize_vector_indexes_sync(self) -> MaintenanceResponse:
        """Synchronous version of optimize_vector_indexes."""
        return asyncio.run(self.optimize_vector_indexes())

    async def collect_statistics(self) -> MaintenanceResponse:
        """
        Trigger background task to collect system usage statistics (admin only).
        
        Returns:
            MaintenanceResponse: Task status information.
        """
        response = await self._client._request("POST", "/admin/maintenance/collect-stats")
        return MaintenanceResponse(**response.json())

    def collect_statistics_sync(self) -> MaintenanceResponse:
        """Synchronous version of collect_statistics."""
        return asyncio.run(self.collect_statistics())

    async def audit_deletion(
        self, entity_type: str, entity_id: str
    ) -> AuditCheckResponse:
        """
        Check the status of a resource scheduled for deletion (admin only).
        
        Args:
            entity_type: The type of the entity (e.g., 'knowledge_base').
            entity_id: The ID of the entity.
            
        Returns:
            AuditCheckResponse: Status of the deletion audit.
        """
        response = await self._client._request(
            "POST", f"/admin/audit/deletions/{entity_type}/{entity_id}"
        )
        return AuditCheckResponse(**response.json())

    def audit_deletion_sync(
        self, entity_type: str, entity_id: str
    ) -> AuditCheckResponse:
        """Synchronous version of audit_deletion."""
        return asyncio.run(self.audit_deletion(entity_type, entity_id))

    async def cleanup_audit_record(self, audit_id: str) -> AuditCleanupResponse:
        """
        Trigger cleanup for an audited resource deletion (admin only).
        
        Args:
            audit_id: The ID of the audit record.
            
        Returns:
            AuditCleanupResponse: Result of the cleanup process.
        """
        response = await self._client._request("POST", f"/admin/audit/cleanup/{audit_id}")
        return AuditCleanupResponse(**response.json())

    def cleanup_audit_record_sync(self, audit_id: str) -> AuditCleanupResponse:
        """Synchronous version of cleanup_audit_record."""
        return asyncio.run(self.cleanup_audit_record(audit_id))

    async def get_audit_record(self, audit_id: str) -> AuditRecordResponse:
        """
        Retrieve a specific deletion audit record by ID (admin only).
        
        Args:
            audit_id: The ID of the audit record.
            
        Returns:
            AuditRecordResponse: The audit record details.
        """
        response = await self._client._request("GET", f"/admin/audit/{audit_id}")
        return AuditRecordResponse(**response.json())

    def get_audit_record_sync(self, audit_id: str) -> AuditRecordResponse:
        """Synchronous version of get_audit_record."""
        return asyncio.run(self.get_audit_record(audit_id))

    async def get_license_status(self) -> LicenseStatusResponse:
        """
        Get the current license status information (admin only).
        
        Returns:
            LicenseStatusResponse: License details.
        """
        response = await self._client._request("GET", "/admin/license")
        return LicenseStatusResponse(**response.json())

    def get_license_status_sync(self) -> LicenseStatusResponse:
        """Synchronous version of get_license_status."""
        return asyncio.run(self.get_license_status())

    # Backup Management Endpoints
    async def list_backups(self) -> Dict[str, Any]:
        """
        List all available backups (admin only).
        
        Returns:
            Dict[str, Any]: List of available backups.
        """
        response = await self._client._request("GET", "/admin/backups")
        return response.json()

    def list_backups_sync(self) -> Dict[str, Any]:
        """Synchronous version of list_backups."""
        return asyncio.run(self.list_backups())

    async def create_backup(self) -> Dict[str, Any]:
        """
        Initiate a database backup (admin only).
        
        Returns:
            Dict[str, Any]: Backup task information.
        """
        response = await self._client._request("POST", "/admin/backups")
        return response.json()

    def create_backup_sync(self) -> Dict[str, Any]:
        """Synchronous version of create_backup."""
        return asyncio.run(self.create_backup())

    async def restore_backup(self, backup_filename: str) -> Dict[str, Any]:
        """
        Restore database from a backup (admin only).
        
        Args:
            backup_filename: The filename of the backup to restore.
            
        Returns:
            Dict[str, Any]: Restore task information.
        """
        response = await self._client._request("POST", f"/admin/backups/{backup_filename}/restore")
        return response.json()

    def restore_backup_sync(self, backup_filename: str) -> Dict[str, Any]:
        """Synchronous version of restore_backup."""
        return asyncio.run(self.restore_backup(backup_filename))

    async def delete_backup(self, backup_filename: str) -> bool:
        """
        Delete a specific backup (admin only).
        
        Args:
            backup_filename: The filename of the backup to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        response = await self._client._request("DELETE", f"/admin/backups/{backup_filename}")
        return response.status_code == 204

    def delete_backup_sync(self, backup_filename: str) -> bool:
        """Synchronous version of delete_backup."""
        return asyncio.run(self.delete_backup(backup_filename))

    async def download_backup(self, backup_filename: str) -> bytes:
        """
        Download a specific backup (admin only).
        
        Args:
            backup_filename: The filename of the backup to download.
            
        Returns:
            bytes: The backup file content.
        """
        response = await self._client._request("GET", f"/admin/backups/{backup_filename}/download")
        return response.content

    def download_backup_sync(self, backup_filename: str) -> bytes:
        """Synchronous version of download_backup."""
        return asyncio.run(self.download_backup(backup_filename))

    # System Monitoring Endpoints
    async def get_rate_limit_stats(self) -> Dict[str, Any]:
        """
        Get current rate limiting statistics (admin only).
        
        Returns:
            Dict[str, Any]: Rate limiting statistics.
        """
        response = await self._client._request("GET", "/admin/rate-limit-stats")
        return response.json()

    def get_rate_limit_stats_sync(self) -> Dict[str, Any]:
        """Synchronous version of get_rate_limit_stats."""
        return asyncio.run(self.get_rate_limit_stats())

    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics (admin only).
        
        Returns:
            Dict[str, Any]: System metrics data.
        """
        response = await self._client._request("GET", "/admin/system-metrics")
        return response.json()

    def get_system_metrics_sync(self) -> Dict[str, Any]:
        """Synchronous version of get_system_metrics."""
        return asyncio.run(self.get_system_metrics())

    async def clear_rate_limit_cache(self) -> Dict[str, Any]:
        """
        Clear rate limiting cache for debugging (admin only).
        
        Returns:
            Dict[str, Any]: Cache clearing result.
        """
        response = await self._client._request("POST", "/admin/clear-rate-limit-cache")
        return response.json()

    def clear_rate_limit_cache_sync(self) -> Dict[str, Any]:
        """Synchronous version of clear_rate_limit_cache."""
        return asyncio.run(self.clear_rate_limit_cache()) 