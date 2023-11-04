import json
import logging
from datetime import datetime

from sqlalchemy.engine import Connectable

from dags.domain.advisory.nvd.cve import convert_to_match_string, UnexpectedFormat
from dags.storage import get_engine, model_as_dict, make_upsert_query
from dags.storage.models import osint
from dags.storage.models.osint import MatchString

logger = logging.getLogger("airflow.task")


def get_latest_update_date() -> datetime:
    engine = get_engine()
    return engine.scalar(
        osint.MatchString.__table__.select()
        .with_only_columns(osint.MatchString.lastModified)
        .order_by(osint.MatchString.lastModified.desc())
        .limit(1)
    )


_insert_batch_size = 3000


def import_file_to_db(conn: Connectable, file_name: str):
    with open(file_name, "r") as f:
        match_strings: list[MatchString] = json.load(f)

    logger.info("downloaded match strings amount: %s", len(match_strings))

    match_strings_to_insert = []
    for match_string in match_strings:
        try:
            match_string_obj = convert_to_match_string(match_string)
            match_strings_to_insert.append(model_as_dict(match_string_obj))
        except (UnexpectedFormat, KeyError) as e:
            logger.exception("failed to convert match string %s", match_string)
            continue

        if len(match_strings_to_insert) >= _insert_batch_size:
            insert_match_strings(conn, match_strings_to_insert)
            match_strings_to_insert.clear()

    insert_match_strings(conn, match_strings_to_insert)


def insert_match_strings(conn: Connectable, match_strings_to_insert: list[dict]):
    if match_strings_to_insert:
        logger.info("inserting %s match strings", len(match_strings_to_insert))
        res = conn.execute(make_upsert_query(osint.MatchString, [osint.MatchString.id]), *match_strings_to_insert)
        logger.info("inserted %s match strings", res.rowcount)
