import logging
from uuid import UUID

from sqlmodel import Session

from app.db_models.address import Country
from app.repositories.address import CountryRepository
from app.schemas.address import CountryCreate, CountryPublic, CountryUpdate

logger = logging.getLogger(__name__)


class CountryService:
    """Service for country metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.country_repo = CountryRepository(session)

    def get_countries(self) -> list[CountryPublic]:
        """Get all active countries formatted for API response"""
        logger.debug("Fetching all active countries")
        countries = self.country_repo.get_active_countries()
        logger.debug(f"Found {len(countries)} active countries")
        return [
            CountryPublic(countryId=country.id, countryName=country.name)
            for country in countries
        ]

    def get_country_by_id(self, country_id: UUID) -> Country | None:
        """Get country by ID"""
        logger.debug(f"Fetching country by ID: {country_id}")
        country = self.country_repo.get_by_id(country_id)
        if country:
            logger.debug(f"Country found: {country.name} (ID: {country_id})")
        else:
            logger.debug(f"Country not found: ID {country_id}")
        return country

    def get_country_by_code(self, code: str) -> Country | None:
        """Get country by ISO code"""
        logger.debug(f"Fetching country by code: {code}")
        country = self.country_repo.get_by_code(code)
        if country:
            logger.debug(f"Country found: {country.name} (code: {code})")
        else:
            logger.debug(f"Country not found with code: {code}")
        return country

    def create_country(self, country_in: CountryCreate) -> Country:
        """Create a new country"""
        logger.info(f"Creating country: {country_in.name} (code: {country_in.code})")
        country = Country(
            name=country_in.name,
            code=country_in.code.upper(),  # Store codes in uppercase
            is_active=country_in.is_active,
        )
        created_country = self.country_repo.create(country)
        logger.info(f"Country created successfully: {created_country.name} (ID: {created_country.id})")
        return created_country

    def update_country(
        self, country: Country, country_update: CountryUpdate
    ) -> Country:
        """Update country information"""
        logger.info(f"Updating country: {country.name} (ID: {country.id})")
        update_data = country_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for country {country.id}: {update_fields}")

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        country.sqlmodel_update(update_data)
        updated_country = self.country_repo.update(country)
        logger.info(f"Country updated successfully: {updated_country.name} (ID: {updated_country.id})")
        return updated_country

    def code_exists(self, code: str, exclude_country_id: UUID | None = None) -> bool:
        """Check if country code exists, optionally excluding a specific country"""
        logger.debug(f"Checking if country code exists: {code}")
        existing_country = self.country_repo.get_by_code(code.upper())
        if not existing_country:
            logger.debug(f"Country code does not exist: {code}")
            return False
        if exclude_country_id and existing_country.id == exclude_country_id:
            logger.debug(f"Country code exists but excluded from check: {code}")
            return False
        logger.debug(f"Country code already exists: {code}")
        return True

    def delete_country(self, country: Country) -> None:
        """Delete a country"""
        logger.warning(f"Deleting country: {country.name} (ID: {country.id})")
        self.country_repo.delete(country)
        logger.info(f"Country deleted successfully: {country.name} (ID: {country.id})")
