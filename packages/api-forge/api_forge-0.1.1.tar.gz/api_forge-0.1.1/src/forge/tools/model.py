"""
ModelForge: Enhanced model management for database entities.
Handles Pydantic and SQLAlchemy model generation, caching, and type mapping.
"""

from typing import Dict, List, Tuple, Type, Any
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Table, inspect, Enum as SQLAlchemyEnum

from forge.gen.enum import EnumInfo, load_enums
from forge.gen.fn import FunctionMetadata, load_fn
from forge.gen.table import BaseSQLModel, load_tables
from forge.gen.view import load_views
from forge.tools.sql_mapping import get_eq_type, JSONBType
from forge.tools.db import DBForge
from forge.core.logging import *


#  todo: Add some utility for the 'exclude_tables' field
class ModelForge(BaseModel):
    """
    Manages model generation and caching for database entities.
    Handles both Pydantic and SQLAlchemy models with support for enums.
    """

    db_manager: DBForge = Field(..., description="Database manager instance")
    include_schemas: List[str] = Field(
        ..., description="Schemas to include in model generation"
    )
    exclude_tables: List[str] = Field(default_factory=list)

    # ^ TABLE cache:    { name: (Table, (PydanticModel, SQLAlchemyModel)) }
    table_cache: Dict[str, Tuple[Table, Tuple[Type[BaseModel], Type[BaseSQLModel]]]] = (
        Field(default_factory=dict)
    )
    # ^ VIEW cache:     { name: (Table, (QueryModel, ResultModel)) }
    view_cache: Dict[str, Tuple[Table, Tuple[Type[BaseModel], Type[BaseModel]]]] = (
        Field(default_factory=dict)
    )
    # ^ ENUM cache:     { name: EnumInfo , ... }
    enum_cache: Dict[str, EnumInfo] = Field(default_factory=dict)
    # ^ FN cache:       { name: FunctionMetadata , ... }
    fn_cache: Dict[str, FunctionMetadata] = Field(default_factory=dict)
    proc_cache: Dict[str, FunctionMetadata] = Field(default_factory=dict)
    trig_cache: Dict[str, FunctionMetadata] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def __init__(self, **data):
        super().__init__(**data)
        self._load_models()
        self._load_enums()
        self._load_views()
        self._load_fn()

    def _load_enums(self) -> None:
        self.enum_cache = load_enums(
            metadata=self.db_manager.metadata,
            engine=self.db_manager.engine,
            include_schemas=self.include_schemas,
            exclude_tables=self.exclude_tables,
        )

    def _load_models(self) -> None:
        self.table_cache = load_tables(
            metadata=self.db_manager.metadata,
            engine=self.db_manager.engine,
            include_schemas=self.include_schemas,
            exclude_tables=self.exclude_tables,
        )

    def _load_views(self) -> None:
        """Load and cache views as Table objects with associated Pydantic models"""
        self.view_cache = load_views(
            metadata=self.db_manager.metadata,
            engine=self.db_manager.engine,
            include_schemas=self.include_schemas,
            db_dependency=self.db_manager.get_db,
        )

    def _load_fn(self) -> None:
        fn, proc, trig = load_fn(
            db_dependency=self.db_manager.get_db, include_schemas=self.include_schemas
        )
        self.fn_cache = fn
        self.proc_cache = proc
        self.trig_cache = trig

    def log_metadata_stats(self) -> None:
        """Print metadata statistics in a table format."""
        inspector = inspect(self.db_manager.engine)
        print(header("ModelForge Statistics"))

        # Table headers
        schema_width = 16
        count_width = 6
        headers = [
            "Schema",
            "Tables",
            "Views",
            "Enums",
            "Fn's",
            "Proc's",
            "Trig's",
            "Total",
        ]
        col_widths = [schema_width] + [count_width] * (len(headers) - 1)

        # Print header row
        header_row = "│ "
        header_row += " │ ".join(
            pad_str(bright(h), w) for h, w in zip(headers, col_widths)
        )
        header_row += " │"

        border_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        top_border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        print(f"\n{top_border}")
        print(header_row)
        print(border_line)

        # Track totals for summary
        total_tables = 0
        total_views = 0
        total_enums = 0
        total_functions = 0
        total_procedures = 0
        total_triggers = 0

        # Print each schema's statistics
        for schema in sorted(self.include_schemas):
            # Count items for this schema
            tables = len(
                [t for t, _ in self.table_cache.values() if t.schema == schema]
            )
            views = len([v for v, _ in self.view_cache.values() if v.schema == schema])
            enums = len([e for e in self.enum_cache.values() if e.schema == schema])
            functions = len([f for f in self.fn_cache.values() if f.schema == schema])
            procedures = len(
                [p for p in self.proc_cache.values() if p.schema == schema]
            )
            triggers = len([t for t in self.trig_cache.values() if t.schema == schema])
            schema_total = tables + views + enums + functions + procedures + triggers

            # Update totals
            total_tables += tables
            total_views += views
            total_enums += enums
            total_functions += functions
            total_procedures += procedures
            total_triggers += triggers

            row = [  # Create row (formatted strings)
                pad_str(magenta(schema), schema_width),
                pad_str(green(str(tables)), count_width, "right"),
                pad_str(blue(str(views)), count_width, "right"),
                pad_str(yellow(str(enums)), count_width, "right"),
                pad_str(magenta(str(functions)), count_width, "right"),
                pad_str(magenta(str(procedures)), count_width, "right"),
                pad_str(magenta(str(triggers)), count_width, "right"),
                pad_str(bright(str(schema_total)), count_width, "right"),
            ]
            print("│ " + " │ ".join(row) + " │")

        # Print summary row
        print(border_line)
        grand_total = (
            total_tables
            + total_views
            + total_enums
            + total_functions
            + total_procedures
            + total_triggers
        )
        summary_row = [
            pad_str(bright("TOTAL"), schema_width),
            pad_str(green(str(total_tables)), count_width, "right"),
            pad_str(blue(str(total_views)), count_width, "right"),
            pad_str(yellow(str(total_enums)), count_width, "right"),
            pad_str(magenta(str(total_functions)), count_width, "right"),
            pad_str(magenta(str(total_procedures)), count_width, "right"),
            pad_str(magenta(str(total_triggers)), count_width, "right"),
            pad_str(underline(bright(str(grand_total))), count_width, "right"),
        ]
        print("│ " + " │ ".join(summary_row) + " │")
        print(bottom_border)
        print()

    def log_schema_tables(self) -> None:
        for schema in self.include_schemas:
            print(f"\n{'Schema:'} {bold(schema)}")
            for table in self.db_manager.metadata.tables.values():
                if table.name in inspect(self.db_manager.engine).get_table_names(
                    schema=schema
                ):
                    print_table_structure(table)

    def log_schema_views(self) -> None:
        for schema in self.include_schemas:
            print(f"\n{'Schema:'} {bold(schema)}")
            for table in self.db_manager.metadata.tables.values():
                if table.name in inspect(self.db_manager.engine).get_view_names(
                    schema=schema
                ):
                    print_table_structure(table)

    def log_schema_fns(self) -> None:
        """Log all functions organized by schema."""
        print(header("Database Functions"))

        # * Group fns by schema
        for schema in sorted(self.include_schemas):
            schema_fns = {
                name: metadata
                for name, metadata in self.fn_cache.items()
                if metadata.schema == schema
            }

            if not schema_fns:
                continue
            print(f"\n{bright('Schema:')} {bold(schema)}")  # Print schema header
            [
                print(f"{fn.__repr__()}\n") for fn in schema_fns.values()
            ]  # * Print the function metadata


def print_table_structure(table: Table) -> None:
    """Print detailed table structure with columns and enums."""

    def get_column_flags(column: Column) -> List[str]:
        """Get formatted flags for a column."""
        flags = []
        if column.primary_key:
            flags.append(f"{green('PK')}")
        if column.foreign_keys:
            ref_table = next(iter(column.foreign_keys)).column.table
            flags.append(f"{blue(f'FK → {ref_table.schema}.{bold(ref_table.name)}')}")
        return flags

    def get_base_type(type_: Any) -> str:
        """Extract base type from Optional types."""
        type_str = str(type_)  # Get the string representation

        if "typing.Optional" in type_str:
            return re.search(r"\[(.*)\]", type_str).group(1).split(".")[-1]

        match isinstance(type_, type):  # Handle non-Optional types
            case True:
                return type_.__name__  # ^ Return class name if it's a type
            case False:
                return str(type_)  # ^ Return string representation otherwise

    # Print table name and comment
    print(f"\t{cyan(table.schema)}.{bold(cyan(table.name))}", end=" ")
    match table.comment:
        case None:
            print()
        case _:
            print(f"({italic(gray(table.comment))})")

    # Print columns
    for column in table.columns:
        flags_str = " ".join(get_column_flags(column))
        py_type = get_eq_type(str(column.type))
        nullable = "" if column.nullable else "*"

        # # Determine type string and values based on column type
        match column.type:
            case _ if isinstance(column.type, SQLAlchemyEnum):
                # type_str = f"{yellow(column.type.name)}"
                type_str = f"{yellow(f'Enum({column.type.name})')}"
                values = f"{gray(str(column.type.enums))}"
            case _:
                values = ""
                if isinstance(py_type, JSONBType):
                    type_str = magenta("JSONB")
                else:
                    type_str = magenta(get_base_type(py_type))

        print(
            f"\t\t{column.name:<24} {red(f'{nullable:<2}')}{gray(str(column.type)[:20]):<32} "
            f"{type_str:<16} {flags_str} {values if values else ''}"
        )

    print()
