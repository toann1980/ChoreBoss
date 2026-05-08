"""Web UI routes for the ChoreBoss FastAPI app."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import create_access_token, get_admin_person, get_current_person, get_session
from choreboss.repositories import ChoreRepository, PeopleRepository
from choreboss.services import ChoreService, PeopleService

router = APIRouter()

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def _ctx(request: Request, **context: Any) -> dict[str, Any]:
    """Build a template context with the FastAPI request/session attached."""
    base: dict[str, Any] = {"request": request, "session": request.session}
    base.update(context)
    return base


def _render(request: Request, template_name: str, status_code: int = 200, **context: Any):
    """Render a Jinja template response."""
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=_ctx(request, **context),
        status_code=status_code,
    )


async def _request_data(request: Request) -> dict[str, Any]:
    """Read JSON or simple form payload from a request."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            return data if isinstance(data, dict) else {"payload": data}
        except Exception:
            return {}

    body = await request.body()
    if not body:
        return {}

    # Avoid depending on python-multipart for basic browser forms.
    parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _truthy(value: Any) -> bool:
    """Normalize common HTML form truthy values."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "on", "yes"}


async def _load_people(session: AsyncSession) -> list[Any]:
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    return await service.get_all_people()


async def _load_chores(session: AsyncSession) -> list[Any]:
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    return await service.get_all_chores()


async def _load_assigned_chores(session: AsyncSession, person_id: int) -> list[Any]:
    chore_repo = ChoreRepository(session)
    return await chore_repo.get_chores_for_person(person_id)


def _due_label(chore: Any) -> str:
    """Build a friendly due-status label for a chore."""
    if getattr(chore, "person_id", None) is None:
        return "Unassigned"
    return "Due now"


@router.get("/", name="index", response_class=HTMLResponse)
async def index(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Render the dashboard shell."""
    chores = await _load_chores(session)
    people = await _load_people(session)
    return _render(request, "index.html", chores=chores, people=people)


@router.get("/login", name="login", response_class=HTMLResponse)
async def login_get(request: Request):
    """Render the login page."""
    if request.session.get("token"):
        return RedirectResponse(url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    return _render(request, "login.html")


@router.post("/login", name="login_post")
async def login_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate a person and create a FastAPI session."""
    data = await _request_data(request)
    login_name = str(data.get("login_name", "")).strip().lower()
    pin = str(data.get("pin", ""))

    if not login_name or not pin:
        return JSONResponse({"error": "Missing login_name or pin"}, status_code=status.HTTP_400_BAD_REQUEST)

    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_login_name(login_name)
    if not person:
        return JSONResponse({"error": "Person not found"}, status_code=status.HTTP_404_NOT_FOUND)

    if not service.verify_pin(pin, person.pin):
        return JSONResponse({"error": "Invalid PIN"}, status_code=status.HTTP_401_UNAUTHORIZED)

    token = create_access_token(person_id=person.id, is_admin=person.is_admin)
    request.session.clear()
    request.session.update(
        {
            "token": token,
            "person_id": person.id,
            "login_name": person.login_name,
            "is_admin": bool(person.is_admin),
        }
    )

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True})

    return RedirectResponse(url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout", name="logout")
async def logout(request: Request):
    """Clear the browser session."""
    request.session.clear()
    return RedirectResponse(url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/chores", name="chores_list", response_class=HTMLResponse)
async def chores_list(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """List chores for the current viewer."""
    is_admin = bool(current_person.get("is_admin"))
    if is_admin:
        chores = await _load_chores(session)
    else:
        chores = await _load_assigned_chores(session, int(current_person["person_id"]))

    chore_rows = []
    for chore in chores:
        chore.due_label = _due_label(chore)
        chore_rows.append(chore)

    return _render(
        request,
        "chores_list.html",
        chores=chore_rows,
        current_person=current_person,
        is_admin=is_admin,
        page_title="Chores List" if is_admin else "My Chores",
        empty_message="No chores? This can't be right..." if is_admin else "No chores assigned to you yet.",
    )


@router.get("/chores/{chore_id:int}", name="chore_detail", response_class=HTMLResponse)
async def chore_detail(
    chore_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """View chore details."""
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)
    if not chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")

    if chore.person_id is not None:
        person = await PeopleService(people_repo).get_person_by_id(chore.person_id)
        if person is not None:
            chore.person_id_foreign_key = person

    if chore.last_completed_id is not None:
        person = await PeopleService(people_repo).get_person_by_id(chore.last_completed_id)
        if person is not None:
            chore.last_completed_id_foreign_key = person

    return _render(request, "chore_detail.html", chore=chore)


@router.get("/chores/add", name="add_chore", response_class=HTMLResponse)
async def add_chore_get(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Render the add chore page."""
    people = await _load_people(session)
    return _render(request, "add_chore.html", people=people)


@router.post("/chores/add", name="add_chore")
async def add_chore_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Create a new chore (admin only)."""
    if not current_person.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    data = await _request_data(request)
    person_id_raw = data.get("person_id") or data.get("assigned_to") or None
    person_id = int(person_id_raw) if person_id_raw not in (None, "") else None

    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.add_chore(
        name=str(data.get("name", "")).strip(),
        description=str(data.get("description", "")).strip(),
        person_id=person_id,
    )
    await session.commit()

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True, "chore_id": chore.id}, status_code=status.HTTP_201_CREATED)

    return RedirectResponse(url=request.url_for("chores_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/chores/{chore_id:int}/edit", name="edit_chore", response_class=HTMLResponse)
async def edit_chore_get(
    chore_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Render the chore edit page."""
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)
    if not chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")
    people = await _load_people(session)
    return _render(request, "edit_chore.html", chore=chore, people=people)


@router.post("/chores/{chore_id:int}/edit", name="edit_chore")
async def edit_chore_post(
    chore_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Update a chore (admin only)."""
    if not current_person.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    data = await _request_data(request)
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)
    if not chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")

    if data.get("name") is not None:
        chore.name = str(data.get("name", "")).strip()
    if data.get("description") is not None:
        chore.description = str(data.get("description", "")).strip()
    if data.get("person_id") not in (None, ""):
        chore.person_id = int(data.get("person_id"))
    else:
        chore.person_id = None

    await service.update_chore(chore)
    await session.commit()

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True})

    return RedirectResponse(url=request.url_for("chore_detail", chore_id=chore_id), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/chores/{chore_id:int}/complete", name="complete_chore")
async def complete_chore(
    chore_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Mark a chore as complete and auto-assign the next person."""
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)
    if not chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")

    result = await service.complete_chore(chore_id, current_person["person_id"])
    await session.commit()

    if "application/json" in request.headers.get("content-type", "") or request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JSONResponse({"success": True, "chore": result})

    return RedirectResponse(url=request.url_for("chore_detail", chore_id=chore_id), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/chores/{chore_id:int}/delete", name="delete_chore")
async def delete_chore(
    chore_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_admin_person),
):
    """Delete a chore (admin only)."""
    chore_repo = ChoreRepository(session)
    people_repo = PeopleRepository(session)
    service = ChoreService(chore_repo, people_repo)
    chore = await service.get_chore_by_id(chore_id)
    if not chore:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")

    await service.delete_chore(chore_id)
    await session.commit()

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True}, status_code=status.HTTP_200_OK)

    return RedirectResponse(url=request.url_for("chores_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/verify_pin", name="verify_pin")
async def verify_pin(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Validate a PIN for modal-driven actions."""
    data = await _request_data(request)
    context = data.get("context")
    pin = data.get("pin")
    if not context or not pin:
        return JSONResponse({"status": "failure"}, status_code=status.HTTP_400_BAD_REQUEST)

    current_login_name = request.session.get("login_name")
    if not current_login_name:
        if context == "add_person":
            people_exist = bool(await _load_people(session))
            if not people_exist:
                return JSONResponse({"status": "success"})
        return JSONResponse({"status": "failure"}, status_code=status.HTTP_401_UNAUTHORIZED)

    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_login_name(str(current_login_name))
    if not person or not service.verify_pin(str(pin), person.pin):
        return JSONResponse({"status": "failure", "reason": "invalid"})

    token = create_access_token(person_id=person.id, is_admin=person.is_admin)
    request.session.update(
        {
            "token": token,
            "person_id": person.id,
            "login_name": person.login_name,
            "is_admin": bool(person.is_admin),
        }
    )

    is_admin = bool(person.is_admin)
    if context == "add_person":
        people_exist = bool(await _load_people(session))
        if is_admin or not people_exist:
            return JSONResponse({"status": "success"})
        return JSONResponse({"status": "failure", "reason": "not_admin"})

    if context == "complete_chore":
        return JSONResponse({"status": "success"})

    if context in {"change_sequence", "delete_chore", "delete_person", "edit_chore", "edit_person"}:
        if is_admin:
            return JSONResponse({"status": "success"})
        return JSONResponse({"status": "failure", "reason": "not_admin"})

    return JSONResponse({"status": "failure", "reason": "invalid"})


@router.get("/people", name="people_list", response_class=HTMLResponse)
async def people_list(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """List all people."""
    people = await _load_people(session)
    return _render(request, "edit_people.html", people=people)


@router.get("/people/{person_id:int}", name="person_detail", response_class=HTMLResponse)
async def person_detail_get(
    person_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Render the edit person page."""
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return _render(request, "edit_person.html", person=person)


@router.post("/people/{person_id:int}", name="person_detail")
async def person_detail_post(
    person_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_admin_person),
):
    """Update a person (admin only)."""
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    data = await _request_data(request)
    if data.get("first_name") is not None:
        person.first_name = str(data.get("first_name", "")).strip()
    if data.get("last_name") is not None:
        person.last_name = str(data.get("last_name", "")).strip()
    if data.get("birthday") is not None:
        from datetime import date

        person.birthday = date.fromisoformat(str(data.get("birthday")))
    if data.get("is_admin") is not None:
        person.is_admin = _truthy(data.get("is_admin"))
    if data.get("assign_chores") is not None:
        person.assign_chores = _truthy(data.get("assign_chores"))

    await service.update_person(person)
    await session.commit()

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True})

    return RedirectResponse(url=request.url_for("person_detail", person_id=person_id), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/people/add", name="add_person", response_class=HTMLResponse)
async def add_person_get(request: Request, session: AsyncSession = Depends(get_session)):
    """Render the add person page."""
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    admins_exist = await service.admins_exist()
    return _render(request, "add_person.html", form_action=str(request.url_for("add_person")), admins_exist=admins_exist)


@router.post("/people/add", name="add_person")
async def add_person_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Create a new person."""
    data = await _request_data(request)
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)

    login_name = str(data.get("login_name", "")).strip().lower()
    if not login_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login name is required")

    if await service.get_person_by_login_name(login_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login name already exists")

    admins_exist = await service.admins_exist()
    current_person = request.session.get("person_id")
    if admins_exist and current_person is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    if admins_exist:
        # Preserve the current rule: adding a person becomes admin-only once admins exist.
        current_session_person = request.session.get("person_id")
        if current_session_person is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if not request.session.get("is_admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    result = await service.add_person(
        first_name=str(data.get("first_name", "")).strip(),
        last_name=str(data.get("last_name", "")).strip(),
        birthday=str(data.get("birthday", "")),
        pin=str(data.get("pin", "")),
        is_admin=_truthy(data.get("is_admin")),
        assign_chores=_truthy(data.get("assign_chores", True)),
        login_name=login_name,
    )
    await session.commit()

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True, "person_id": result.id}, status_code=status.HTTP_201_CREATED)

    return RedirectResponse(url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/people/{person_id:int}/delete", name="delete_person")
async def delete_person(
    person_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_admin_person),
):
    """Delete a person (admin only)."""
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    await service.delete_person(person_id)
    await session.commit()

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True})

    return RedirectResponse(url=request.url_for("people_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/people/{person_id:int}/edit_pin", name="edit_pin", response_class=HTMLResponse)
async def edit_pin_get(
    person_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Render the PIN edit page."""
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    if current_person["person_id"] != person_id and not current_person.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    return _render(request, "edit_pin.html", person=person)


@router.post("/people/{person_id:int}/edit_pin", name="edit_pin")
async def edit_pin_post(
    person_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Update a person's PIN."""
    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    person = await service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    if current_person["person_id"] != person_id and not current_person.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    data = await _request_data(request)
    current_pin = str(data.get("current_pin", ""))
    new_pin = str(data.get("new_pin", ""))
    confirm_pin = str(data.get("confirm_pin", ""))

    if not service.verify_pin(current_pin, person.pin):
        return _render(request, "edit_pin.html", person=person, error="Current PIN is incorrect.", status_code=status.HTTP_400_BAD_REQUEST)
    if new_pin != confirm_pin:
        return _render(request, "edit_pin.html", person=person, error="New PINs do not match.", status_code=status.HTTP_400_BAD_REQUEST)
    if not service.validate_pin(new_pin):
        return _render(request, "edit_pin.html", person=person, error="PIN must be 4 to 6 digits.", status_code=status.HTTP_400_BAD_REQUEST)

    person.set_pin(new_pin)
    await service.update_person(person)
    await session.commit()

    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True})

    return RedirectResponse(url=request.url_for("person_detail", person_id=person_id), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/change_sequence", name="change_sequence", response_class=HTMLResponse)
async def change_sequence_get(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_current_person),
):
    """Render the change-sequence page."""
    people = await _load_people(session)
    return _render(request, "change_sequence.html", people=people)


@router.post("/change_sequence", name="change_sequence")
async def change_sequence_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_admin_person),
):
    """Compatibility handler for direct form posts."""
    people = await _load_people(session)
    return _render(
        request,
        "change_sequence.html",
        people=people,
        error="Sequence updates are handled by Save Sequence.",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@router.post("/update_sequence", name="update_sequence")
async def update_sequence(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_person: dict[str, Any] = Depends(get_admin_person),
):
    """Apply a reordered person sequence."""
    data = await _request_data(request)
    seq_raw = data.get("sequence_data") or data.get("payload") or data
    if isinstance(seq_raw, str):
        import json

        try:
            seq = json.loads(seq_raw)
        except Exception:
            seq = None
    else:
        seq = seq_raw

    if isinstance(seq, dict) and "sequence_data" in seq:
        seq = seq["sequence_data"]
        if isinstance(seq, str):
            import json

            try:
                seq = json.loads(seq)
            except Exception:
                seq = None

    if not isinstance(seq, list):
        return JSONResponse({"error": "Bad sequence data"}, status_code=status.HTTP_400_BAD_REQUEST)

    people_repo = PeopleRepository(session)
    service = PeopleService(people_repo)
    try:
        for item in seq:
            await service.update_sequence(int(item["id"]), int(item["sequence"]))
    except Exception:
        return JSONResponse({"error": "Failed to update sequence", "status": "failure"}, status_code=status.HTTP_400_BAD_REQUEST)

    await session.commit()
    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True, "status": "success"})
    return RedirectResponse(url=request.url_for("people_list"), status_code=status.HTTP_303_SEE_OTHER)

