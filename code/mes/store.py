"""MES Work Order Store Module

This module provides in-memory storage for manufacturing work orders.
It manages the persistence and retrieval of WorkOrder objects for the MES system.

In a production system, this would likely be replaced with a database or distributed cache,
but for this simulation, an in-memory store is sufficient to demonstrate the orchestration logic.
"""
from mes.models import WorkOrder


class InMemoryMesStore:
    """In-memory storage for manufacturing work orders.
    
    This store maintains work orders indexed by their unique identifiers,
    providing simple save and retrieval operations for the MES orchestration system.
    
    Attributes:
        workorders: Dictionary mapping workorder_id to WorkOrder objects
    """
    def __init__(self) -> None:
        # Dictionary to store work orders with workorder_id as the key
        self.workorders: dict[str, WorkOrder] = {}

    def save(self, workorder: WorkOrder) -> None:
        """Save or update a work order in the store.
        
        Args:
            workorder: The WorkOrder object to save
        """
        # Add or overwrite the work order using its unique identifier as the key
        self.workorders[workorder.workorder_id] = workorder

    def get(self, workorder_id: str) -> WorkOrder:
        """Retrieve a work order by its identifier.
        
        Args:
            workorder_id: The unique identifier of the work order to retrieve
            
        Returns:
            The WorkOrder object associated with the given ID
            
        Raises:
            KeyError: If no work order exists with the given ID
        """
        # Return the work order from the dictionary (raises KeyError if not found)
        return self.workorders[workorder_id]


# Singleton instance of InMemoryMesStore used throughout the application
mes_store = InMemoryMesStore()