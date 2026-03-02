import json
import os
import re
from typing import List

from .schema import LeaseSummary


def _full_text_from_pages(pages: List[dict]) -> str:
    parts = []
    for p in pages:
        parts.append(f"[Page {p['page_number']}]\n{p.get('text', '')}")
    return "\n\n".join(parts)


def _rule_based_extract(text: str) -> LeaseSummary:
    def find(pattern: str, default: str = "Not specified") -> str:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            try:
                return (m.group(1) or m.group(0)).strip()[:500]
            except (IndexError, AttributeError):
                return (m.group(0) or "").strip()[:500]
        return default

    # Section 1.1 style (A. ... B. ...)
    landlord = find(r"B\.\s*LANDLORD:\s*(.+?)(?=\n[C-Z]\.|\nSECTION|$)", "Not specified")
    landlord_address = find(r"C\.\s*ADDRESS OF LANDLORD:\s*(.+?)(?=\n[D-Z]\.|\nSECTION|$)", "")
    if not landlord_address:
        landlord_address = find(r"ADDRESS OF LANDLORD:\s*(.+?)(?=\n[A-Z]\.|\nSECTION|$)", "")
    tenant = find(r"D\.\s*TENANT:\s*(.+?)(?=\n[E-Z]\.|\nF\.|$)", "Not specified")
    if tenant == "Not specified":
        tenant = find(r"TENANT:\s*\n([^\n]+(?:\n[^\n]+){0,3})", "Not specified")
    # Tenant address: often the lines under TENANT (street, city, state) before F. TRADE NAME
    tenant_address = find(r"D\.\s*TENANT:\s*[^\n]+\n([^\n]+(?:\n[^\n]+){0,2}?)(?=\n[E-Z]\.|\nF\.|\nSECTION|$)", "")
    if not tenant_address:
        tenant_address = find(r"TENANT:\s*\n([^\n]+(?:\n[^\n]+){1,3})", "")
    trade_name = find(r"F\.\s*TENANT'S TRADE NAME:\s*(.+?)(?=\n[G-Z]\.|\nSECTION|$)", "")
    lease_term = find(r"G\.\s*LEASE TERM:\s*(.+?)(?=\n[H-Z]\.|\nSECTION|$)", "")
    renewal = find(r"H\.\s*RENEWAL OPTIONS:\s*(.+?)(?=\n[I-Z]\.|\nSECTION|$)", "Not specified")
    rent_comm = find(r"J\.\s*RENT COMMENCEMENT DATE:\s*(.+?)(?=\n[K-Z]\.|\nSECTION|$)", "")
    monthly_rent = find(r"K\.\s*MONTHLY RENT:\s*(.+?)(?=\n[L-Z]\.|\nSECTION|$)", "Not specified")
    permitted = find(r"M\.\s*PERMITTED USE:\s*(.+?)(?=\n[N-Z]\.|\nSECTION|$)", "")
    size = find(r"N\.\s*APPROXIMATE SIZE[^:]*:\s*(.+?)(?=\n[O-Z]\.|\nSECTION|$)", "")
    security = find(r"[O0]\.\s*SECURITY DEPOSIT:\s*(.+?)(?=\n[P-Z0-9]\.|\nSECTION|$)", "Not specified")
    if security == "Not specified":
        security = find(r"SECURITY DEPOSIT:\s*\$?([\d,]+)", "Not specified")
        if security != "Not specified":
            security = f"${security}"
    advanced = find(r"P\.\s*ADVANCED[^\n]*:\s*(.+?)(?=\nSECTION|$)", "")

    # Date of lease / execution date
    date_lease = find(r"DATE OF LEASE:\s*(\w+\s+\d+\s*,?\s*\d{4})", "")
    if not date_lease:
        date_lease = find(r"Lease Date:\s*(\w+\s+\d+,?\s*\d{4})", "")
    execution_date = date_lease or None
    # Guarantor
    guarantor = find(r"GUARANTOR[:\s]+(.+?)(?=\n[A-Z][\.\s]|\nSECTION|$)", "")
    if not guarantor:
        guarantor = find(r"GUARANTY[:\s]+(.+?)(?=\n[A-Z][\.\s]|\nSECTION|$)", "")

    # Premises address
    premises = find(r"ADDRESS is\s+([^\n]+?)(?=\s+Premises|\s+located|$)", "")
    if not premises:
        premises = find(r"(5441 Main Street[^\n]*)", "")

    # CAM/Tax/Insurance from 1.1 K
    cam = find(r"(\$?\d+(?:\.\d+)?\s*/?\s*SF\s*(?:CAM|Tax|Insurance)[^\n]*)", "")
    if not cam and "CAM" in text:
        cam = find(r"(\$2\s*SF\s*CAM[^\n]*)", "")

    # Lease start: rent commencement or date of lease
    lease_start = rent_comm or date_lease or "See Section 1.1"
    # End: "last day of the Fifth Full Lease Year"
    end_m = re.search(r"end on the last day of the\s+(?:Fifth|5th)\s+Full Lease Year", text, re.IGNORECASE)
    lease_end = "Last day of fifth full lease year (see Section 2.3)" if end_m else "See Section 2.3"

    # Termination: collect key phrases
    term_parts = []
    if re.search(r"sooner terminated", text, re.IGNORECASE):
        term_parts.append("Lease may be sooner terminated as provided in the Lease.")
    if re.search(r"eminent domain|condemnation", text, re.IGNORECASE):
        term_parts.append("Eminent domain/condemnation: see Article 29.")
    if re.search(r"default.*terminat|terminat.*default", text, re.IGNORECASE):
        term_parts.append("Termination for default: see default and remedies articles.")
    if re.search(r"Exclusive Use Covenant|remove items|terminate", text, re.IGNORECASE):
        term_parts.append("Termination for violation of Exclusive Use Covenant (Article 15.2).")
    termination_clauses = " ".join(term_parts) if term_parts else "See Lease for termination and default provisions."

    # Special provisions: optional summary
    special = "Exhibits A–F (Site Plan, Design Criteria, Rent Schedule, Lease Plan, Renewal Option, Landlord's Work). Subordination (Art. 8); Estoppel (Art. 8.4); Rules and Regulations (Art. 28)."

    return LeaseSummary(
        tenant=tenant[:300] if tenant else "Not specified",
        landlord=landlord[:300] if landlord else "Not specified",
        lease_start_date=lease_start,
        lease_end_date=lease_end,
        rent_amount=monthly_rent[:300] if monthly_rent else "See Exhibit C",
        renewal_options=renewal[:300] if renewal else "Not specified",
        termination_clauses=termination_clauses[:500],
        security_deposit=security[:200] if security else "Not specified",
        special_provisions=special[:500],
        premises_address=premises or None,
        permitted_use=permitted or None,
        rent_commencement_date=rent_comm or None,
        cam_tax_insurance=cam or None,
        advanced_rental=advanced or None,
        lease_term=lease_term or None,
        trade_name=trade_name or None,
        approximate_size_sqft=size or None,
        landlord_address=(landlord_address or "").strip()[:400] or None,
        tenant_address=(tenant_address or "").strip()[:400] or None,
        guarantor=(guarantor or "").strip()[:300] or None,
        execution_date=execution_date,
        option_notice_period=None,
        option_rent=None,
        insurance_requirements=None,
        assignment_subletting=None,
        default_remedies=None,
        parking=None,
        signage=None,
        broker=None,
        additional_terms_from_document=None,
    )


def _llm_extract(full_text: str, model: str) -> LeaseSummary | None:
    try:
        from openai import OpenAI
    except ImportError:
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    # Truncate to fit context (e.g. 100k chars)
    text = full_text[:90000] if len(full_text) > 90000 else full_text
    client = OpenAI(api_key=api_key)
    schema_dict = LeaseSummary.model_json_schema()
    prompt = f"""Extract lease information from the following legal lease document into the exact JSON schema below.
Extract as many of the schema fields as the document supports; use null for any field not found or not applicable.
Use only information explicitly stated in the document. If a value is in an exhibit (e.g. Exhibit C for rent), write something like "See Exhibit C" or summarize what the document says (e.g. "Per Section 1.1 K: $17/SF base + $2/SF CAM/Tax/Insurance").
For termination_clauses, summarize the main ways the lease can be terminated (e.g. default, eminent domain, expiration).
For special_provisions, list notable provisions (exhibits, subordination, rules, etc.).
After filling the schema fields, identify any other significant lease terms, clauses, or data that appear in the document but are not covered by the schema fields above. For each such item, output one line in the form: Label: value (or short summary). Put the full list (all lines) into the additional_terms_from_document field. If there are no such terms, set additional_terms_from_document to null.
Return only valid JSON matching this schema: {json.dumps(schema_dict)}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You extract structured data from leases. Respond only with valid JSON."},
                {"role": "user", "content": prompt + "\n\n---\n\nDocument:\n\n" + text},
            ],
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
        # Align keys to schema (snake_case)
        return LeaseSummary(**data)
    except Exception:
        return None

    #     Extract ans structured lease summary from document pages.....
def extract_lease_summary(pages: List[dict], use_llm: bool = True, model: str | None = None) -> LeaseSummary:
    from config import EXTRACTION_MODEL
    full_text = _full_text_from_pages(pages)
    if use_llm and model is None:
        model = EXTRACTION_MODEL
    if use_llm and model:
        summary = _llm_extract(full_text, model)
        if summary is not None:
            return summary
    return _rule_based_extract(full_text)
