"""
This module contains custom logging handlers.
"""

from __future__ import annotations

import logging
import sqlite3
import sys
import traceback
import uuid
from importlib.resources import as_file, files
from typing import Any

from bug_trail_core.exceptions import (
    create_exception_instance_table,
    create_exception_type_table,
    create_traceback_info_table,
    insert_exception_instance,
    insert_exception_type,
    insert_traceback_info,
)
from bug_trail_core.sqlite3_utils import is_table_empty, serialize_to_sqlite_supported
from bug_trail_core.system_info import create_system_info_table, record_system_info
from bug_trail_core.venv_info import create_python_libraries_table, record_venv_info


class BaseErrorLogHandler:
    """
    A custom logging handler that logs to a SQLite database.
    """

    def __init__(
        self, db_path: str, pico: bool = False, minimum_level: int = logging.ERROR, single_threaded: bool = True
    ) -> None:
        """
        Initialize the handler
        Args:
            db_path (str): Path to the SQLite database
        """
        self.single_threaded = single_threaded
        self.db_path = db_path
        self.pico = pico
        self.minimum_level = minimum_level
        self.create_table_sql: str = ""
        self.formatted_sql = ""
        self.field_names = ""
        # call things only after all attributes assigned
        self.reopen()
        self.create_table()
        self.reopen()
        create_exception_type_table(self.conn)
        self.reopen()
        create_exception_instance_table(self.conn)
        self.reopen()
        create_traceback_info_table(self.conn)

        self.reopen()
        create_system_info_table(self.conn)
        self.reopen()
        if is_table_empty(self.conn, "system_info"):
            record_system_info(self.conn)

        self.reopen()
        create_python_libraries_table(self.conn)
        self.reopen()
        if is_table_empty(self.conn, "python_libraries"):
            record_venv_info(self.conn)

    def reopen(self) -> None:
        """Reopen the connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode = MEMORY;")
        self.conn.execute("PRAGMA synchronous = OFF;")

    def create_table(self) -> None:
        """
        Create the logs table if it doesn't exist
        """
        # Locate the resource file
        source = files("bug_trail_core").joinpath("create_table.sql")

        with as_file(source) as file:
            self.create_table_sql = file.read_text(encoding="utf-8")

        if not self.create_table_sql:
            # Create a dummy LogRecord to introspect its attributes
            dummy_record = None

            # Define a mapping of Python types to SQLite types
            type_mapping = {
                int: "INTEGER",
                float: "REAL",
                str: "TEXT",
                bytes: "BLOB",  # Assuming bytes should be stored as BLOB
                type(None): "TEXT",  # Why would we have a column of just None?
            }

            # Build the columns schema based on LogRecord attributes
            columns = []

            dummy_record = logging.LogRecord(
                name="", level=logging.ERROR, pathname="", lineno=0, msg="", args=(), exc_info=None
            )
            for attr in dir(dummy_record):
                if not callable(getattr(dummy_record, attr)) and not attr.startswith("__"):
                    attr_type = type(getattr(dummy_record, attr, ""))
                    sqlite_type = type_mapping.get(attr_type, "TEXT")  # Default to TEXT if type not in mapping
                    columns.append(f"{attr} {sqlite_type}")

            # Add traceback column
            columns.append("traceback TEXT")

            # message is when `msg % args` gets evaluated by some part of the `logging` module?
            if "message TEXT" not in columns:
                columns.append("message TEXT")

            columns_text = ", ".join(columns)
            self.create_table_sql = f"CREATE TABLE IF NOT EXISTS logs ({columns_text})"
        # TODO: is there a faster way to check if a table exist?
        self.safe_execute(self.create_table_sql, [])

    def emit(self, record: logging.LogRecord) -> None:
        """
        Insert a log record into the database

        Args:
            record (logging.LogRecord): The log record to be inserted
        """
        if record.levelno < self.minimum_level:
            return

        # clientside primary key
        record_id = str(uuid.uuid4())
        if not record.exc_info:
            record.exc_info = sys.exc_info()
        # Check if there is exception information
        if record.exc_info:
            exception_type, exception, traceback_object = record.exc_info
            # Format the traceback
            traceback_str = "".join(traceback.format_exception(*record.exc_info))
            record.traceback = traceback_str

            if exception:
                # not unique per log entry
                insert_exception_type(self.conn, exception)
                # unique per log entry
                insert_exception_instance(self.conn, record_id, exception)
                exception_instance_id = record_id
                # Insert traceback info
                if exception and exception.__traceback__:
                    insert_traceback_info(self.conn, exception_instance_id, exception.__traceback__)
        else:
            record.traceback = None

        if not self.formatted_sql:
            # I don't think I can precalc this in advance as the fields in a Record
            # can change subtly from call to call.
            insert_sql = "INSERT INTO logs ({fields}) VALUES ({values})"
            self.field_names = ", ".join(
                [attr for attr in dir(record) if not attr.startswith("__") and not attr == "getMessage"]
            )
            self.field_names = self.field_names + ", traceback, message"
            field_values = ", ".join(["?" for _ in self.field_names.split(", ")])
            self.formatted_sql = insert_sql.format(fields="record_id," + self.field_names, values="?," + field_values)
        args = [record_id] + [getattr(record, field, "") for field in self.field_names.split(", ")]
        args = [serialize_to_sqlite_supported(arg) for arg in args]

        self.safe_execute(self.formatted_sql, args)

    def safe_execute(self, sql: str, args: list[Any], recurse_count: int = 0) -> None:
        if not self.single_threaded:
            self.reopen()
        try:
            self.conn.execute(sql, args)
        except sqlite3.OperationalError as oe:
            if "no such table" in oe.args[0] and recurse_count == 0:
                self.create_table()
                recurse_count += 1
                self.safe_execute(sql, args, recurse_count)
            else:
                raise
        self.conn.commit()
        if not self.single_threaded:
            self.conn.close()

    def close(self) -> None:
        """
        Close the connection to the database
        """
        # If we are not single threaded, even talking to the conn object
        # will throw an error.
        if self.conn and self.single_threaded:
            try:
                self.conn.close()
            except sqlite3.ProgrammingError as programming_error:
                if "Cannot operate on a closed database" in str(programming_error):
                    pass
                raise


class BugTrailHandler(logging.Handler):
    """
    A custom logging handler that logs to a SQLite database.
    """

    def __init__(self, db_path: str, minimum_level: int = logging.ERROR, single_threaded: bool = True) -> None:
        """
        Initialize the handler
        Args:
            db_path (str): Path to the SQLite database
            single_threaded (bool): If True, the handler will close the connection after each emit.
        """
        self.base_handler = BaseErrorLogHandler(db_path, minimum_level=minimum_level, single_threaded=single_threaded)
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Insert a log record into the database

        Args:
            record (logging.LogRecord): The log record to be inserted
        """
        self.base_handler.emit(record)

    def close(self) -> None:
        """
        Close the connection to the database
        """
        self.base_handler.close()
        super().close()
