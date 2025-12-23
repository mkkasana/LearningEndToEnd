from uuid import UUID

from sqlmodel import Session

from app.db_models.address import Country
from app.repositories.address import CountryRepository
from app.schemas.address import CountryCreate, CountryPublic, CountryUpdate


class CountryService:
    """Service for country metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.country_repo = CountryRepository(session)

    def get_countries(self) -> list[CountryPublic]:
        """Get all active countries formatted for API response"""
        countries = self.country_repo.get_active_countries()
        return [
            CountryPublic(countryId=country.id, countryName=country.name)
            for country in countries
        ]

    def get_country_by_id(self, country_id: UUID) -> Country | None:
        """Get country by ID"""
        return self.country_repo.get_by_id(country_id)

    def get_country_by_code(self, code: str) -> Country | None:
        """Get country by ISO code"""
        return self.country_repo.get_by_code(code)

    def create_country(self, country_in: CountryCreate) -> Country:
        """Create a new country"""
        country = Country(
            name=country_in.name,
            code=country_in.code.upper(),  # Store codes in uppercase
            is_active=country_in.is_active,
        )
        return self.country_repo.create(country)

    def update_country(self, country: Country, country_update: CountryUpdate) -> Country:
        """Update country information"""
        update_data = country_update.model_dump(exclude_unset=True)
        
        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        
        country.sqlmodel_update(update_data)
        return self.country_repo.update(country)

    def code_exists(self, code: str, exclude_country_id: UUID | None = None) -> bool:
        """Check if country code exists, optionally excluding a specific country"""
        existing_country = self.country_repo.get_by_code(code.upper())
        if not existing_country:
            return False
        if exclude_country_id and existing_country.id == exclude_country_id:
            return False
        return True

    def delete_country(self, country: Country) -> None:
        """Delete a country"""
        self.country_repo.delete(country)
