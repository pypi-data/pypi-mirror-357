# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project: data-service-sdk-python
# @Author: qm
# @Date: 2025/6/24 12:01
# @Description:


"""
Common data models for PyGard client.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Bbox2D(BaseModel):
    """2D bounding box model."""

    min_x: Optional[float] = Field(None, description="Minimum X coordinate")
    min_y: Optional[float] = Field(None, description="Minimum Y coordinate")
    max_x: Optional[float] = Field(None, description="Maximum X coordinate")
    max_y: Optional[float] = Field(None, description="Maximum Y coordinate")


class VerticalRange(BaseModel):
    """Vertical range model."""

    min_z: Optional[float] = Field(None, description="Minimum Z coordinate")
    max_z: Optional[float] = Field(None, description="Maximum Z coordinate")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class RevisionHistory(BaseModel):
    """Revision history model."""

    version: str = Field(..., description="Version number")
    time: datetime = Field(..., description="Revision date")
    message: str = Field(..., description="Revision description")
    editor: Optional[str] = Field(None, description="Author of the revision")


class Other(BaseModel):
    """Other metadata model."""

    # This is a flexible model for additional metadata
    # Using Dict[str, Any] to accommodate various JSON structures
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access."""
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-like assignment."""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default."""
        return self.data.get(key, default)

    def keys(self):
        """Get all keys."""
        return self.data.keys()

    def values(self):
        """Get all values."""
        return self.data.values()

    def items(self):
        """Get all items."""
        return self.data.items()
