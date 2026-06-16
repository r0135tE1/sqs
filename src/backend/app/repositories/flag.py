from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Flag


class FlagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_all(self, flags: list[dict]) -> None:
        """Insert or overwrite all flags. Each dict needs: code, name, flag_svg (bytes)."""
        now = datetime.now(timezone.utc)
        stmt = pg_insert(Flag).values([
            {"code": f["code"], "name": f["name"], "flag_svg": f["flag_svg"], "extracted_at": now}
            for f in flags
        ])
        stmt = stmt.on_conflict_do_update(
            index_elements=["code"],
            set_={
                "name": stmt.excluded.name,
                "flag_svg": stmt.excluded.flag_svg,
                "extracted_at": stmt.excluded.extracted_at,
            },
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_all(self) -> list[Flag]:
        result = await self.db.execute(select(Flag))
        return list(result.scalars().all())
