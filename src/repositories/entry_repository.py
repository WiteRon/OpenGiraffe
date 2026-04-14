"""Repository for entries table access."""

from typing import List, Optional

from ..config.settings import Settings
from ..db.connection import get_db_connection
from ..domain.entry import EntryCreate, EntryResponse, EntryUpdate, LocationResponse


def _model_to_dict(model, exclude_unset=False):
    """Support both Pydantic v1 and v2 model serialization."""

    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=exclude_unset)
    return model.dict(exclude_unset=exclude_unset)


class EntryRepository:
    """Read/write access to travel entries."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def list_locations(self):
        """Return grouped locations with coordinates for globe markers."""

        query = """
            SELECT
                destination,
                country,
                city,
                lat,
                lng,
                COUNT(*) AS count,
                MAX(entry_date) AS latest_entry_date
            FROM entries
            WHERE city IS NOT NULL
              AND lat IS NOT NULL
              AND lng IS NOT NULL
            GROUP BY destination, country, city, lat, lng
            ORDER BY latest_entry_date DESC, city ASC
        """
        with get_db_connection(self.settings) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
        return [LocationResponse(**row) for row in rows]

    def list_entries(
        self,
        destination=None,
        city=None,
        country=None,
        entry_date=None,
    ):
        """Return entries filtered by the provided query parameters."""

        conditions = []  # type: List[str]
        params = []  # type: List[str]

        if destination:
            conditions.append("destination = %s")
            params.append(destination)
        if city:
            conditions.append("city = %s")
            params.append(city)
        if country:
            conditions.append("country = %s")
            params.append(country)
        if entry_date:
            conditions.append("entry_date = %s")
            params.append(entry_date)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT
                id,
                destination,
                entry_date,
                entry_type,
                category,
                country,
                city,
                lat,
                lng,
                title,
                content,
                created_at,
                updated_at
            FROM entries
            {where_clause}
            ORDER BY entry_date DESC, id DESC
        """

        with get_db_connection(self.settings) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
        return [EntryResponse(**row) for row in rows]

    def get_entry(self, entry_id):
        """Fetch a single entry by id."""

        query = """
            SELECT
                id,
                destination,
                entry_date,
                entry_type,
                category,
                country,
                city,
                lat,
                lng,
                title,
                content,
                created_at,
                updated_at
            FROM entries
            WHERE id = %s
        """
        with get_db_connection(self.settings) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (entry_id,))
                row = cursor.fetchone()
        return EntryResponse(**row) if row else None

    def create_entry(self, entry: EntryCreate) -> EntryResponse:
        """Insert a new entry and return the created row."""

        payload = _model_to_dict(entry)
        query = """
            INSERT INTO entries (
                destination,
                entry_date,
                entry_type,
                category,
                country,
                city,
                lat,
                lng,
                title,
                content
            ) VALUES (
                %(destination)s,
                %(entry_date)s,
                %(entry_type)s,
                %(category)s,
                %(country)s,
                %(city)s,
                %(lat)s,
                %(lng)s,
                %(title)s,
                %(content)s
            )
        """
        with get_db_connection(self.settings) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, payload)
                entry_id = cursor.lastrowid
        created = self.get_entry(entry_id)
        if created is None:
            raise RuntimeError("Created entry could not be loaded")
        return created

    def update_entry(self, entry_id, entry):
        """Update an existing entry and return the updated row."""

        payload = _model_to_dict(entry, exclude_unset=True)
        if not payload:
            return self.get_entry(entry_id)

        assignments = ", ".join(f"{field} = %s" for field in payload.keys())
        params = list(payload.values()) + [entry_id]
        query = f"UPDATE entries SET {assignments} WHERE id = %s"

        with get_db_connection(self.settings) as connection:
            with connection.cursor() as cursor:
                affected = cursor.execute(query, params)
        if affected == 0:
            return None
        return self.get_entry(entry_id)

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by id."""

        query = "DELETE FROM entries WHERE id = %s"
        with get_db_connection(self.settings) as connection:
            with connection.cursor() as cursor:
                affected = cursor.execute(query, (entry_id,))
        return affected > 0
