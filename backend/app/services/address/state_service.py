from uuid import UUID

from sqlmodel import Session

from app.db_models.address import State
from app.repositories.address import StateRepository
from app.schemas.address import StateCreate, StatePublic, StateUpdate


class StateService:
    """Service for state metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.state_repo = StateRepository(session)

    def get_states_by_country(self, country_id: UUID) -> list[StatePublic]:
        """Get all active states for a country formatted for API response"""
        states = self.state_repo.get_by_country(country_id)
        return [StatePublic(stateId=state.id, stateName=state.name) for state in states]

    def get_state_by_id(self, state_id: UUID) -> State | None:
        """Get state by ID"""
        return self.state_repo.get_by_id(state_id)

    def create_state(self, state_in: StateCreate) -> State:
        """Create a new state"""
        state = State(
            name=state_in.name,
            code=state_in.code.upper() if state_in.code else None,
            country_id=state_in.country_id,
            is_active=state_in.is_active,
        )
        return self.state_repo.create(state)

    def update_state(self, state: State, state_update: StateUpdate) -> State:
        """Update state information"""
        update_data = state_update.model_dump(exclude_unset=True)

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        state.sqlmodel_update(update_data)
        return self.state_repo.update(state)

    def code_exists(
        self, code: str, country_id: UUID, exclude_state_id: UUID | None = None
    ) -> bool:
        """Check if state code exists within a country, optionally excluding a specific state"""
        if not code:
            return False
        existing_state = self.state_repo.get_by_code(code.upper(), country_id)
        if not existing_state:
            return False
        if exclude_state_id and existing_state.id == exclude_state_id:
            return False
        return True

    def delete_state(self, state: State) -> None:
        """Delete a state"""
        self.state_repo.delete(state)
