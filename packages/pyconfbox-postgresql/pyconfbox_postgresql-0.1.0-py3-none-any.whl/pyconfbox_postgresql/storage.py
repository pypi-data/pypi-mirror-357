"""PostgreSQL storage backend for PyConfBox."""

import json
from typing import Any, Dict, List, Optional

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

try:
    from pyconfbox.core.exceptions import StorageError
    from pyconfbox.core.types import ConfigValue
    from pyconfbox.storage.base import BaseStorage
except ImportError:
    raise ImportError("pyconfbox is required for pyconfbox-postgresql plugin")


class PostgreSQLStorage(BaseStorage):
    """PostgreSQL database storage backend for PyConfBox.

    This storage backend uses PostgreSQL database to persist configuration values.
    Requires psycopg2-binary package to be installed.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        database: str = "pyconfbox",
        table: str = "configurations",
        **kwargs: Any
    ) -> None:
        """Initialize PostgreSQL storage.

        Args:
            host: PostgreSQL server host.
            port: PostgreSQL server port.
            user: PostgreSQL username.
            password: PostgreSQL password.
            database: Database name.
            table: Table name for storing configurations.
            **kwargs: Additional connection parameters.
        """
        super().__init__()

        if psycopg2 is None:
            raise ImportError(
                "psycopg2-binary package is required for PostgreSQL storage. "
                "Install it with: pip install psycopg2-binary"
            )

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.connection_params = kwargs

        self._connection = None
        self._ensure_database()
        self._ensure_table()

    def _get_connection(self):
        """Get PostgreSQL database connection."""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    **self.connection_params
                )
                self._connection.autocommit = True
            except Exception as e:
                raise StorageError(f"Failed to connect to PostgreSQL: {e}")

        return self._connection

    def _ensure_database(self) -> None:
        """Ensure the database exists."""
        try:
            # Connect to default database to create target database if needed
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database='postgres',  # Default database
                **self.connection_params
            )
            connection.autocommit = True

            with connection.cursor() as cursor:
                # Check if database exists
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (self.database,)
                )

                if not cursor.fetchone():
                    cursor.execute(f'CREATE DATABASE "{self.database}"')

            connection.close()
        except Exception:
            # Database might already exist or we don't have permission to create it
            pass

    def _ensure_table(self) -> None:
        """Ensure the configurations table exists."""
        connection = self._get_connection()

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS "{self.table}" (
            "key" VARCHAR(255) PRIMARY KEY,
            "value" TEXT,
            "data_type" VARCHAR(50),
            "scope" VARCHAR(50),
            "storage" VARCHAR(50),
            "immutable" BOOLEAN DEFAULT FALSE,
            "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Create indexes
        create_indexes_sql = [
            f'CREATE INDEX IF NOT EXISTS "idx_{self.table}_scope" ON "{self.table}" ("scope")',
            f'CREATE INDEX IF NOT EXISTS "idx_{self.table}_storage" ON "{self.table}" ("storage")'
        ]

        # Create update trigger function
        create_trigger_sql = f"""
        CREATE OR REPLACE FUNCTION update_{self.table}_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trigger_update_{self.table}_updated_at ON "{self.table}";
        CREATE TRIGGER trigger_update_{self.table}_updated_at
            BEFORE UPDATE ON "{self.table}"
            FOR EACH ROW
            EXECUTE FUNCTION update_{self.table}_updated_at();
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(create_table_sql)

                for index_sql in create_indexes_sql:
                    cursor.execute(index_sql)

                cursor.execute(create_trigger_sql)

        except Exception as e:
            raise StorageError(f"Failed to create table: {e}")

    def get(self, key: str) -> Optional[ConfigValue]:
        """Get a configuration value from PostgreSQL.

        Args:
            key: Configuration key.

        Returns:
            Configuration value if found, None otherwise.
        """
        connection = self._get_connection()

        try:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    f'SELECT * FROM "{self.table}" WHERE "key" = %s',
                    (key,)
                )
                row = cursor.fetchone()

                if row:
                    # Parse JSON value
                    try:
                        value = json.loads(row['value'])
                    except (json.JSONDecodeError, TypeError):
                        value = row['value']

                    return ConfigValue(
                        key=row['key'],
                        value=value,
                        data_type=row['data_type'],
                        scope=row['scope'],
                        storage=row['storage'],
                        immutable=bool(row['immutable']),
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )

                return None

        except Exception as e:
            raise StorageError(f"Failed to get value from PostgreSQL: {e}")

    def set(self, key: str, value: ConfigValue) -> None:
        """Set a configuration value in PostgreSQL.

        Args:
            key: Configuration key.
            value: Configuration value to store.
        """
        connection = self._get_connection()

        # Serialize value to JSON
        try:
            serialized_value = json.dumps(value.value, ensure_ascii=False)
        except (TypeError, ValueError):
            serialized_value = str(value.value)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO "{self.table}"
                    ("key", "value", "data_type", "scope", "storage", "immutable", "created_at", "updated_at")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT ("key") DO UPDATE SET
                    "value" = EXCLUDED."value",
                    "data_type" = EXCLUDED."data_type",
                    "scope" = EXCLUDED."scope",
                    "storage" = EXCLUDED."storage",
                    "immutable" = EXCLUDED."immutable",
                    "updated_at" = CURRENT_TIMESTAMP
                """, (
                    key,
                    serialized_value,
                    value.data_type,
                    value.scope,
                    value.storage,
                    value.immutable,
                    value.created_at,
                    value.updated_at
                ))

        except Exception as e:
            raise StorageError(f"Failed to set value in PostgreSQL: {e}")

    def delete(self, key: str) -> bool:
        """Delete a configuration value from PostgreSQL.

        Args:
            key: Configuration key.

        Returns:
            True if deleted, False if not found.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f'DELETE FROM "{self.table}" WHERE "key" = %s',
                    (key,)
                )
                return cursor.rowcount > 0

        except Exception as e:
            raise StorageError(f"Failed to delete value from PostgreSQL: {e}")

    def exists(self, key: str) -> bool:
        """Check if a configuration key exists in PostgreSQL.

        Args:
            key: Configuration key.

        Returns:
            True if exists, False otherwise.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f'SELECT 1 FROM "{self.table}" WHERE "key" = %s LIMIT 1',
                    (key,)
                )
                return cursor.fetchone() is not None

        except Exception as e:
            raise StorageError(f"Failed to check existence in PostgreSQL: {e}")

    def keys(self) -> List[str]:
        """Get all configuration keys from PostgreSQL.

        Returns:
            List of configuration keys.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT "key" FROM "{self.table}"')
                return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            raise StorageError(f"Failed to get keys from PostgreSQL: {e}")

    def clear(self) -> None:
        """Clear all configuration values from PostgreSQL."""
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(f'DELETE FROM "{self.table}"')

        except Exception as e:
            raise StorageError(f"Failed to clear PostgreSQL storage: {e}")

    def update(self, data: Dict[str, ConfigValue]) -> None:
        """Update multiple configuration values in PostgreSQL.

        Args:
            data: Dictionary of configuration values.
        """
        for key, value in data.items():
            self.set(key, value)

    def get_info(self) -> Dict[str, Any]:
        """Get information about the PostgreSQL storage.

        Returns:
            Storage information dictionary.
        """
        connection = self._get_connection()

        try:
            with connection.cursor() as cursor:
                # Get table info
                cursor.execute(f'SELECT COUNT(*) FROM "{self.table}"')
                total_keys = cursor.fetchone()[0]

                # Get PostgreSQL version
                cursor.execute("SELECT version()")
                pg_version = cursor.fetchone()[0]

                return {
                    'type': 'postgresql',
                    'host': self.host,
                    'port': self.port,
                    'database': self.database,
                    'table': self.table,
                    'postgresql_version': pg_version,
                    'total_keys': total_keys
                }

        except Exception as e:
            return {
                'type': 'postgresql',
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'table': self.table,
                'error': str(e)
            }

    def close(self) -> None:
        """Close the PostgreSQL connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    def __del__(self) -> None:
        """Cleanup when storage is destroyed."""
        self.close()
