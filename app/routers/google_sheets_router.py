from fastapi import routing


sheets_router = routing.APIRouter()


@sheets_router.post("/get-emails", response_model=EmailList)