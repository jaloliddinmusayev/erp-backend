from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


def _get_client(db: Session, company_id: int, client_id: int) -> Client:
    row = db.get(Client, client_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Client not found.")
    return row


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    s = value.strip()
    return s or None


def _apply_payload(row: Client, payload: ClientCreate | ClientUpdate) -> None:
    email_val = str(payload.email).lower().strip() if payload.email is not None else None
    row.code = payload.code.strip()
    row.name = payload.name.strip()
    row.client_type = payload.client_type
    row.inn = payload.inn.strip() if payload.inn else None
    row.legal_name = _strip_optional(payload.legal_name)
    row.contact_person = _strip_optional(payload.contact_person)
    row.phone = payload.phone
    row.email = email_val
    row.region = _strip_optional(payload.region)
    row.city = _strip_optional(payload.city)
    row.district = _strip_optional(payload.district)
    row.address = payload.address
    row.latitude = payload.latitude
    row.longitude = payload.longitude
    row.bank_name = _strip_optional(payload.bank_name)
    row.bank_account = payload.bank_account
    row.bank_mfo = payload.bank_mfo
    row.notes = payload.notes
    row.is_active = payload.is_active


def create_client(db: Session, company_id: int, payload: ClientCreate) -> Client:
    row = Client(company_id=company_id)
    _apply_payload(row, payload)
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        msg = str(exc.orig) if exc.orig else ""
        if "uq_clients_company_inn" in msg:
            raise ConflictError("Client INN already exists for this company.") from None
        raise ConflictError("Client code already exists for this company.") from None
    db.refresh(row)
    return row


def list_clients(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[Client]:
    stmt = select(Client).where(Client.company_id == company_id)
    if is_active is not None:
        stmt = stmt.where(Client.is_active == is_active)
    if search and (t := search.strip()):
        term = f"%{t}%"
        stmt = stmt.where(
            or_(
                Client.code.ilike(term),
                Client.name.ilike(term),
                Client.phone.ilike(term),
                Client.inn.ilike(term),
                Client.legal_name.ilike(term),
                Client.email.ilike(term),
                Client.contact_person.ilike(term),
                Client.region.ilike(term),
                Client.city.ilike(term),
                Client.district.ilike(term),
            )
        )
    stmt = stmt.order_by(Client.id).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).all())


def get_client(db: Session, company_id: int, client_id: int) -> Client:
    return _get_client(db, company_id, client_id)


def update_client(db: Session, company_id: int, client_id: int, payload: ClientUpdate) -> Client:
    row = _get_client(db, company_id, client_id)
    _apply_payload(row, payload)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        msg = str(exc.orig) if exc.orig else ""
        if "uq_clients_company_inn" in msg:
            raise ConflictError("Client INN already exists for this company.") from None
        raise ConflictError("Client code already exists for this company.") from None
    db.refresh(row)
    return row


def deactivate_client(db: Session, company_id: int, client_id: int) -> Client:
    row = _get_client(db, company_id, client_id)
    row.is_active = False
    db.commit()
    db.refresh(row)
    return row
