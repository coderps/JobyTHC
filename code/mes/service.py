"""MES Orchestrator Service Module

This module provides the main MES (Manufacturing Execution System) service that coordinates
the manufacturing workflow. It delegates to specialized orchestrators for different stages
of the workflow to keep code modular and maintainable.

The service acts as the central router for events from orders, CNC operations, and quality
inspection, dispatching them to the appropriate orchestrator based on event type.
"""
from mes.orchestrators import (
    order_orchestrator,
    cnc_orchestrator,
    quality_orchestrator,
)


class MesOrchestratorService:
    """Main MES service that coordinates the manufacturing orchestration.
    
    This service routes incoming events to specialized orchestrators:
    - OrderCreatedEvent -> OrderOrchestrator
    - CncJobCompletedEvent -> CncOrchestrator
    - QualityInspectionCompletedEvent -> QualityOrchestrator
    
    By delegating to specialized orchestrators, this service maintains a clean separation
    of concerns and keeps each orchestrator focused on its specific workflow stage.
    """

    async def handle_order_created(self, raw_event: dict) -> None:
        """Handle an order creation event by delegating to OrderOrchestrator.
        
        Args:
            raw_event: The OrderCreatedEvent payload as a dictionary
        """
        await order_orchestrator.handle_order_created(raw_event)

    async def handle_cnc_job_completed(self, raw_event: dict) -> None:
        """Handle a CNC job completion event by delegating to CncOrchestrator.
        
        Args:
            raw_event: The CncJobCompletedEvent payload as a dictionary
        """
        await cnc_orchestrator.handle_cnc_job_completed(raw_event)

    async def handle_quality_inspection_completed(self, raw_event: dict) -> None:
        """Handle a quality inspection completion event by delegating to QualityOrchestrator.
        
        Args:
            raw_event: The QualityInspectionCompletedEvent payload as a dictionary
        """
        await quality_orchestrator.handle_quality_inspection_completed(raw_event)


# Singleton instance of the MES service used throughout the application
mes_service = MesOrchestratorService()