from app.models.schemas import UserContext


class IdentityService:
    def __init__(self) -> None:
        self._users = {
            "viewer_1": UserContext(user_id="viewer_1", role="viewer", display_name="Vera Viewer", team="public"),
            "analyst_1": UserContext(user_id="analyst_1", role="analyst", display_name="Ari Analyst", team="operations"),
            "architect_1": UserContext(user_id="architect_1", role="architect", display_name="Alex Architect", team="platform"),
            "admin_1": UserContext(user_id="admin_1", role="admin", display_name="Ada Admin", team="governance"),
        }

    def resolve(self, user_id: str) -> UserContext | None:
        return self._users.get(user_id)

    def list_users(self) -> list[UserContext]:
        return list(self._users.values())
