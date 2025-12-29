import logging
from uuid import UUID

from sqlmodel import Session

from app.db_models.address import State
from app.repositories.address import StateRepository
from app.schemas.address import StateCreate, StatePublic, StateUpdate

logger = logging.getLogger(__name__)


class StateService:
    """Service for state metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.state_repo = StateRepository(session)

    def get_states_by_country(self, country_id: UUID) -> list[StatePublic]:
        """Get all active states for a country formatted for API response"""
        logger.debug(f"Fetching states for country ID: {country_id}")
        states = self.state_repo.get_by_country(country_id)
        logger.debug(f"Found {len(states)} states for country {country_id}")
        return [StatePublic(stateId=state.id, stateName=state.name) for state in states]

    def get_state_by_id(self, state_id: UUID) -> State | None:
        """Get state by ID"""
        logger.debug(f"Fetching state by ID: {state_id}")
        state = self.state_repo.get_by_id(state_id)
        if state:
            logger.debug(f"State found: {state.name} (ID: {state_id})")
        else:
            logger.debug(f"State not found: ID {state_id}")
        return state

    def create_state(self, state_in: StateCreate) -> State:
        """Create a new state"""
        logger.info(f"Creating state: {state_in.name} for country {state_in.country_id}")
        state = State(
            name=state_in.name,
            code=state_in.code.upper() if state_in.code else None,
            country_id=state_in.country_id,
            is_active=state_in.is_active,
        )
        created_state = self.state_repo.create(state)
        logger.info(f"State created successfully: {created_state.name} (ID: {created_state.id})")
        return created_state

    def update_state(self, state: State, state_update: StateUpdate) -> State:
        """Update state information"""
        logger.info(f"Updating state: {state.name} (ID: {state.id})")
        update_data = state_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for state {state.id}: {update_fields}")

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        state.sqlmodel_update(update_data)
        updated_state = self.state_repo.update(state)
        logger.info(f"State updated successfully: {updated_state.name} (ID: {updated_state.id})")
        return updated_state

    def code_exists(
        self, code: str, country_id: UUID, exclude_state_id: UUID | None = None
    ) -> bool:
        """Check if state code exists within a country, optionally excluding a specific state"""
        if not code:
            return False
        logger.debug(f"Checking if state code exists: {code} in country {country_id}")
        existing_state = self.state_repo.get_by_code(code.upper(), country_id)
        if not existing_state:
            logger.debug(f"State code does not exist: {code}")
            return False
        if exclude_state_id and existing_state.id == exclude_state_id:
            logger.debug(f"State code exists but excluded from check: {code}")
            return False
        logger.debug(f"State code already exists: {code}")
        return True

    def delete_state(self, state: State) -> None:
        """Delete a state"""
        logger.warning(f"Deleting state: {state.name} (ID: {state.id})")
        self.state_repo.delete(state)
        logger.info(f"State deleted successfully: {state.name} (ID: {state.id})")
