from __future__ import annotations
import datetime
import json
import logging
import typing
from collections import defaultdict

from sqlalchemy import nulls_last, select, or_, and_, func
from sqlalchemy.engine import Connectable
from sqlalchemy.exc import SQLAlchemyError

from dags.domain.advisory import AdvisoryType, Severity
from dags.domain.advisory.nvd.cve import (
    Vulnerability,
    convert_to_advisory,
    convert_to_vulnerability,
    UnexpectedFormat,
)
from dags.domain.attestations import VulnerabilityScanner
from dags.storage import make_upsert_query, get_engine, model_as_dict
from dags.storage.models import osint

if typing.TYPE_CHECKING:
    from dags.domain import grype

logger = logging.getLogger("airflow.task")


def get_latest_update_date() -> datetime.datetime:
    engine = get_engine()
    return engine.scalar(
        osint.VulAdvisory.__table__.select()
        .where(osint.VulAdvisory.lastModified > "1970-01-01")
        .with_only_columns(osint.VulAdvisory.lastModified)
        .order_by(nulls_last(osint.VulAdvisory.lastModified.desc()))
        .limit(1)
    )


def get_latest_pub_date() -> datetime.datetime:
    engine = get_engine()
    return engine.scalar(
        osint.VulAdvisory.__table__.select()
        .where(osint.VulAdvisory.lastModified > "1970-01-01")
        .with_only_columns(osint.VulAdvisory.publishedOn)
        .order_by(nulls_last(osint.VulAdvisory.publishedOn.desc()))
        .limit(1)
    )


def get_cve_latest_update_date(cve_id: str) -> datetime.datetime:
    engine = get_engine()
    return engine.scalar(
        osint.VulAdvisory.__table__.select()
        .where(osint.VulAdvisory.vulId == cve_id)
        .with_only_columns(osint.VulAdvisory.lastModified)
        .order_by(nulls_last(osint.VulAdvisory.lastModified.desc()))
        .limit(1)
    )


INSERT_BATCH_SIZE = 3000


def import_nvd_file_to_db(conn: Connectable, file_name: str):
    with open(file_name, "r") as f:
        vulns: list[Vulnerability] = json.load(f)

    logger.info("downloaded vulnerabilities amount: %s", len(vulns))

    # TODO(anton): insert file into temp table and import with `insert... from select... on update`
    advisories_to_insert = []
    vulns_to_insert = []
    for vuln in vulns:
        try:
            # https://nvd.nist.gov/vuln/vulnerability-status#divNvdStatus
            if vuln["cve"]["vulnStatus"].lower() == "rejected":
                logger.info("skip rejected vulnerability %s", vuln["cve"]["id"])
                continue

            adv, severity = convert_to_advisory(vuln)
            if severity is None:
                # severity may be None for some statuses
                logger.info("skip vulnerability %s without severity", vuln["cve"]["id"])
                continue
            vuln_obj = convert_to_vulnerability(vuln)
            vuln_obj.severity = severity

            if adv.source == AdvisoryType.NVD31:
                vuln_obj.cvssScore = adv.baseScore

            vulns_to_insert.append(model_as_dict(vuln_obj))
            advisories_to_insert.append(model_as_dict(adv))
        except (UnexpectedFormat, KeyError) as e:
            logger.exception("failed to convert vulnerability %s", vuln)
            continue

        if len(vulns_to_insert) >= INSERT_BATCH_SIZE:
            _insert_nvd_vuln_advisories(vulns_to_insert, advisories_to_insert, conn)
            vulns_to_insert.clear()
            advisories_to_insert.clear()

    _insert_nvd_vuln_advisories(vulns_to_insert, advisories_to_insert, conn)


def _insert_nvd_vuln_advisories(vulns_to_insert: list[dict], advisories_to_insert: list[dict], conn: Connectable):
    if vulns_to_insert:
        logger.info("inserting %s vulnerabilities", len(vulns_to_insert))
        res = conn.execute(
            make_upsert_query(
                osint.Vulnerability,
                [osint.Vulnerability.id],
            ),
            *vulns_to_insert,
        )

        logger.info("inserted vulnerabilities: %s", res.rowcount)

    if advisories_to_insert:
        logger.info("inserting %s advisories", len(advisories_to_insert))
        res = conn.execute(
            make_upsert_query(
                osint.VulAdvisory,
                [
                    osint.VulAdvisory.vulId,
                    osint.VulAdvisory.source,
                    osint.VulAdvisory.lastModified,
                ],
            ),
            *advisories_to_insert,
        )
        logger.info("inserted advisories: %s", res.rowcount)


def save_grype_report(data: dict, attestation_id: int, team_id: int):
    vulns, comp_vulns, vuln_advisories = extract_data_from_grype_report(data)
    if not vulns:
        return

    engine = get_engine()
    total_comp_vulns = 0
    saved_comp_vulns = 0

    with engine.begin() as transaction:
        current_timestamp = transaction.execute(select(func.current_timestamp())).scalar()
        transaction.execute(
            make_upsert_query(
                osint.Vulnerability,
                [osint.Vulnerability.id],
                upsert_cols=[osint.Vulnerability.severity],
            ),
            *[model_as_dict(v) for v in vulns],
        )

        if vuln_advisories:
            transaction.execute(
                make_upsert_query(
                    osint.VulAdvisory,
                    [
                        osint.VulAdvisory.vulId,
                        osint.VulAdvisory.source,
                        osint.VulAdvisory.lastModified,
                    ],
                ),
                *[model_as_dict(v) for v in vuln_advisories],
            )

        for (name, version, type_, purl), vuln_ids in comp_vulns.items():
            total_comp_vulns += len(vuln_ids)
            res = transaction.execute(
                select(osint.Component.id).where(
                    osint.Component.teamId == team_id,
                    or_(
                        osint.Component.purl == purl,
                        and_(
                            osint.Component.name == name,
                            osint.Component.version == version,
                            osint.Component.group == type_,
                        ),
                    ),
                )
            )
            try:
                component_id = res.scalar_one()
            except SQLAlchemyError as e:
                logger.error(
                    "error when trying to find component=%s, its vulnerabilities=%s, error=%s",
                    purl,
                    vuln_ids,
                    e,
                )
                continue
            to_insert = []
            for vuln, fixed_in in vuln_ids:
                created_date = transaction.execute(
                    select(osint.VulComponent.created).where(
                        osint.VulComponent.component == component_id,
                        osint.VulComponent.vulId == vuln,
                        osint.VulComponent.deleted.is_(None),
                    )
                ).scalar()
                to_insert.append(
                    {
                        osint.VulComponent.component.key: component_id,
                        osint.VulComponent.vulId.key: vuln,
                        osint.VulComponent.fixedInVersion.key: fixed_in,
                        osint.VulComponent.created.key: created_date or current_timestamp,
                        osint.VulComponent.source.key: VulnerabilityScanner.GRYPE,
                    }
                )
            saved_comp_vulns += len(to_insert)
            res = transaction.execute(
                make_upsert_query(
                    osint.VulComponent,
                    [
                        osint.VulComponent.component,
                        osint.VulComponent.vulId,
                        osint.VulComponent.created,
                    ],
                    upsert_cols=[osint.VulComponent.fixedInVersion],
                ),
                *to_insert,
            )
            if len(to_insert) != res.rowcount:
                logger.warning(
                    "inserted %s rows, expected %s\n" "component=%s, vuln_ids=%s",
                    res.rowcount,
                    len(to_insert),
                    component_id,
                    vuln_ids,
                )

    if total_comp_vulns != saved_comp_vulns:
        logger.warning(
            "saved %s out of %s component vulnerabilities",
            saved_comp_vulns,
            total_comp_vulns,
        )


PURL = str
ComponentName = str
ComponentVersion = str
ComponentType = str
ComponentDefinition = [ComponentName, ComponentVersion, ComponentType, PURL]
FixedVersion = str
ComponentToVulnerabilities = dict[ComponentDefinition, list[tuple[FixedVersion, FixedVersion]]]


def extract_data_from_grype_report(
    report: grype.Report,
) -> tuple[list[osint.Vulnerability], ComponentToVulnerabilities, list[osint.VulAdvisory]]:
    vulns: dict[str, osint.Vulnerability] = {}
    vul_advisories: list[osint.VulAdvisory] = []
    comp_to_vulns: ComponentToVulnerabilities = defaultdict(list)

    def extract_vuln(
        vuln: grype.Vulnerability | grype.RelatedVulnerabilitiesItem,
    ) -> tuple[str | None, str]:
        if vulns.get(vuln["id"]) is not None:
            return None, ""

        fixed_in_version = ""
        if vuln.get("fix", {}).get("state") == "fixed":
            fixed_in_version = vuln["fix"]["versions"][0]
        vulns[vuln["id"]] = osint.Vulnerability(
            id=vuln["id"],
            severity=Severity.from_str(vuln["severity"]),
        )
        return vuln["id"], fixed_in_version

    for m in report["matches"]:
        vuln_id, fixed_version = extract_vuln(m["vulnerability"])
        if vuln_id is None:
            continue
        if vuln_id.startswith("GHSA") and len(m.get("relatedVulnerabilities") or []) > 0:
            try:
                related = m["relatedVulnerabilities"][0]
                cvss = related["cvss"][0]
                baseScore = cvss["metrics"]["baseScore"]
                vulns[vuln_id].cvssScore = baseScore
                lastModified = get_cve_latest_update_date(related["id"])
                vul_advisories.append(
                    osint.VulAdvisory(
                        vulId=vuln_id,
                        source=AdvisoryType.GHSA,
                        lastModified=lastModified or datetime.datetime.now(),
                        hyperLinks=related["urls"],
                        vector=cvss["vector"],
                        baseScore=baseScore,
                        advisoryText=related["description"],
                        info=related,
                        cpes=[],
                    )
                )
            except Exception:
                logger.warning("error when parsing GHSA advisory: %s", m["relatedVulnerabilities"])

        comp = m["artifact"]
        key = (comp["name"], comp["version"], comp["type"], comp["purl"])
        comp_to_vulns[key].append((vuln_id, fixed_version))

    return list(vulns.values()), comp_to_vulns, vul_advisories
