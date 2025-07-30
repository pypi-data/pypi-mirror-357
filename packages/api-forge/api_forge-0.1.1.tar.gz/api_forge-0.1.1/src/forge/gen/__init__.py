import json
from typing import Callable, List, Dict, Any, Optional, Type, Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Table
from uuid import UUID
from pydantic import BaseModel, create_model, Field
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum as PyEnum

from forge.tools.sql_mapping import *


class CRUD:
    """Class to handle CRUD operations with FastAPI routes."""

    def __init__(
        self,
        table: Table,
        pydantic_model: Type[BaseModel],
        sqlalchemy_model: Type[Any],
        router: APIRouter,
        db_dependency: Callable,
        prefix: str = "",
    ):
        """Initialize CRUD handler with common parameters."""
        self.table = table
        self.pydantic_model = pydantic_model
        self.sqlalchemy_model = sqlalchemy_model
        self.router = router
        self.db_dependency = db_dependency
        self.prefix = prefix

        # Create query params model once for reuse
        self.query_params = self._create_query_params()

    def _create_query_params(self) -> Type[BaseModel]:
        """Create a Pydantic model for query parameters."""
        query_fields = {}

        for column in self.table.columns:
            field_type = get_eq_type(str(column.type))

            # Always make query parameters Optional[str] for JSONB and Array types
            if isinstance(field_type, (JSONBType, ArrayType)):
                query_fields[column.name] = (Optional[str], Field(default=None))
            else:
                # For other types, preserve the type but make it optional
                if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                    # If field is already Optional
                    query_fields[column.name] = (field_type, Field(default=None))
                else:
                    # Make field Optional
                    query_fields[column.name] = (
                        Optional[field_type],
                        Field(default=None),
                    )

        # Create the query params model
        return create_model(
            f"{self.pydantic_model.__name__}QueryParams",
            **query_fields,
            __base__=BaseModel,
        )

    def _get_route_path(self, operation: str = "") -> str:
        """Generate route path with optional prefix."""
        base_path = f"/{self.table.name.lower()}"
        if operation:
            base_path = f"AAA{base_path}/{operation}"
        return f"{self.prefix}{base_path}"

    def create(self) -> None:
        """Add CREATE route."""

        @self.router.post(
            self._get_route_path(),
            response_model=self.pydantic_model,
            summary=f"Create {self.table.name}",
            description=f"Create a new {self.table.name} record",
        )
        def create_resource(
            resource: self.pydantic_model, db: Session = Depends(self.db_dependency)
        ) -> self.pydantic_model:
            data = resource.model_dump(exclude_unset=True)

            # . Why do I think this will be a good idea???
            # . Why do I think this will be a good idea???
            # . Why do I think this will be a good idea???
            # .____.
            # * Only remove the primary key UUID if it exists, keep foreign key UUIDs
            # for column in self.table.columns:
            #     if column.type.python_type == UUID and column.primary_key:
            #         data.pop(column.name, None)

            try:
                db_resource = self.sqlalchemy_model(**data)
                db.add(db_resource)
                db.commit()
                db.refresh(db_resource)
                result_dict = {
                    column.name: getattr(db_resource, column.name)
                    for column in self.table.columns
                }
                return self.pydantic_model(**result_dict)
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=400, detail=f"Creation failed: {str(e)}"
                )

    def read(self) -> None:
        """Add READ route with enhanced JSONB handling."""

        @self.router.get(
            self._get_route_path(),
            response_model=List[self.pydantic_model],
            summary=f"Get {self.table.name} resources",
            description=f"Retrieve {self.table.name} records with optional filtering",
        )
        def read_resources(
            db: Session = Depends(self.db_dependency),
            filters: self.query_params = Depends(),
        ) -> List[self.pydantic_model]:
            query = db.query(self.sqlalchemy_model)
            filters_dict = filters.model_dump(exclude_unset=True)

            # Build query with filters
            for field_name, value in filters_dict.items():
                if value is not None:
                    column = getattr(self.sqlalchemy_model, field_name)
                    field_type = get_eq_type(str(column.type))

                    if isinstance(field_type, (JSONBType, ArrayType)):
                        # Skip JSONB and array filtering for now
                        # You could add custom JSONB filtering logic here if needed
                        continue
                    elif isinstance(column.type, SQLAlchemyEnum):
                        if isinstance(value, str):
                            query = query.filter(column == value)
                        elif isinstance(value, PyEnum):
                            query = query.filter(column == value.value)
                    else:
                        query = query.filter(column == value)

            # Execute query and process results
            resources = query.all()
            processed_records = []

            for resource in resources:
                record_dict = {}
                for column in self.table.columns:
                    value = getattr(resource, column.name)
                    field_type = get_eq_type(str(column.type))

                    if isinstance(field_type, JSONBType):
                        if value is not None:
                            # Parse JSONB data if it's a string
                            if isinstance(value, str):
                                try:
                                    record_dict[column.name] = json.loads(value)
                                except json.JSONDecodeError:
                                    record_dict[column.name] = value
                            else:
                                record_dict[column.name] = value
                        else:
                            record_dict[column.name] = None
                    elif isinstance(field_type, ArrayType):
                        if value is not None:
                            if isinstance(value, str):
                                # Handle PostgreSQL array string format
                                cleaned_value = value.strip("{}").split(",")
                                record_dict[column.name] = [
                                    field_type.item_type(item.strip('"'))
                                    for item in cleaned_value
                                    if item.strip()
                                ]
                            elif isinstance(value, list):
                                record_dict[column.name] = [
                                    field_type.item_type(item)
                                    for item in value
                                    if item is not None
                                ]
                            else:
                                record_dict[column.name] = value
                        else:
                            record_dict[column.name] = []
                    else:
                        record_dict[column.name] = value

                # Validate the processed record
                try:
                    validated_record = self.pydantic_model.model_validate(record_dict)
                    processed_records.append(validated_record)
                except Exception as e:
                    print(
                        f"Validation error for record in {self.table.name}: {record_dict}"
                    )
                    print(f"Error: {str(e)}")
                    raise

            return processed_records

    # todo: Fix the return "updated_data"
    # todo: - The "updated_data" currently returns [] for all cases
    # todo: - But the "old_data" returns the correct data (old data before update)
    def update(self) -> None:
        """Add UPDATE route."""

        @self.router.put(
            self._get_route_path(),
            response_model=Dict[str, Any],
            summary=f"Update {self.table.name}",
            description=f"Update {self.table.name} records that match the filter criteria",
        )
        def update_resource(
            resource: self.pydantic_model,
            db: Session = Depends(self.db_dependency),
            filters: self.query_params = Depends(),
        ) -> Dict[str, Any]:
            update_data = resource.model_dump(exclude_unset=True)
            filters_dict = filters.model_dump(exclude_unset=True)

            if not filters_dict:
                raise HTTPException(status_code=400, detail="No filters provided")

            try:
                query = db.query(self.sqlalchemy_model)
                for attr, value in filters_dict.items():
                    if value is not None:
                        query = query.filter(
                            getattr(self.sqlalchemy_model, attr) == value
                        )

                old_data = [
                    self.pydantic_model.model_validate(data.__dict__)
                    for data in query.all()
                ]

                if not old_data:
                    raise HTTPException(
                        status_code=404, detail="No matching resources found"
                    )

                updated_count = query.update(update_data)
                db.commit()

                updated_data = [
                    self.pydantic_model.model_validate(data.__dict__)
                    for data in query.all()
                ]

                return {
                    "updated_count": updated_count,
                    "old_data": [d.model_dump() for d in old_data],
                    "updated_data": [d.model_dump() for d in updated_data],
                }
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

    def delete(self) -> None:
        """Add DELETE route."""

        @self.router.delete(
            self._get_route_path(),
            response_model=Dict[str, Any],
            summary=f"Delete {self.table.name}",
            description=f"Delete {self.table.name} records that match the filter criteria",
        )
        def delete_resource(
            db: Session = Depends(self.db_dependency),
            filters: self.query_params = Depends(),
        ) -> Dict[str, Any]:
            filters_dict = filters.model_dump(exclude_unset=True)

            if not filters_dict:
                raise HTTPException(status_code=400, detail="No filters provided")

            query = db.query(self.sqlalchemy_model)
            for attr, value in filters_dict.items():
                if value is not None:
                    query = query.filter(getattr(self.sqlalchemy_model, attr) == value)

            try:
                # Get resources before deletion
                to_delete = query.all()
                if not to_delete:
                    return {"message": "No resources found matching the criteria"}

                # Store the data before deletion
                deleted_resources = [
                    self.pydantic_model.model_validate(resource.__dict__).model_dump()
                    for resource in to_delete
                ]

                # Perform deletion
                deleted_count = query.delete(synchronize_session=False)
                db.commit()

                return {
                    "message": f"{deleted_count} resource(s) deleted successfully",
                    "deleted_resources": deleted_resources,
                }
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=400, detail=f"Deletion failed: {str(e)}"
                )

    def generate_all(self) -> None:
        """Generate all CRUD routes."""
        # print(f"\tGen {gray("CRUD")} -> {self.table.name}")
        self.create()
        self.read()
        self.update()
        self.delete()
