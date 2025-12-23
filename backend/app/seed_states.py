"""Seed script to populate state data"""
import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.country import Country
from app.db_models.state import State


def seed_indian_states() -> None:
    """Seed Indian states as an example"""

    with Session(engine) as session:
        # Get India's country ID
        india = session.exec(select(Country).where(Country.code == "IND")).first()

        if not india:
            print("India not found in countries. Please seed countries first.")
            return

        # Check if states already exist for India
        existing_states = session.exec(
            select(State).where(State.country_id == india.id)
        ).first()
        if existing_states:
            print("Indian states already seeded. Skipping...")
            return

        # Indian states and union territories
        indian_states = [
            {"name": "Andaman and Nicobar Islands", "code": "AN"},
            {"name": "Andhra Pradesh", "code": "AP"},
            {"name": "Arunachal Pradesh", "code": "AR"},
            {"name": "Assam", "code": "AS"},
            {"name": "Bihar", "code": "BR"},
            {"name": "Chandigarh", "code": "CH"},
            {"name": "Chhattisgarh", "code": "CT"},
            {"name": "Dadra and Nagar Haveli and Daman and Diu", "code": "DH"},
            {"name": "Delhi", "code": "DL"},
            {"name": "Goa", "code": "GA"},
            {"name": "Gujarat", "code": "GJ"},
            {"name": "Haryana", "code": "HR"},
            {"name": "Himachal Pradesh", "code": "HP"},
            {"name": "Jammu and Kashmir", "code": "JK"},
            {"name": "Jharkhand", "code": "JH"},
            {"name": "Karnataka", "code": "KA"},
            {"name": "Kerala", "code": "KL"},
            {"name": "Ladakh", "code": "LA"},
            {"name": "Lakshadweep", "code": "LD"},
            {"name": "Madhya Pradesh", "code": "MP"},
            {"name": "Maharashtra", "code": "MH"},
            {"name": "Manipur", "code": "MN"},
            {"name": "Meghalaya", "code": "ML"},
            {"name": "Mizoram", "code": "MZ"},
            {"name": "Nagaland", "code": "NL"},
            {"name": "Odisha", "code": "OR"},
            {"name": "Puducherry", "code": "PY"},
            {"name": "Punjab", "code": "PB"},
            {"name": "Rajasthan", "code": "RJ"},
            {"name": "Sikkim", "code": "SK"},
            {"name": "Tamil Nadu", "code": "TN"},
            {"name": "Telangana", "code": "TG"},
            {"name": "Tripura", "code": "TR"},
            {"name": "Uttar Pradesh", "code": "UP"},
            {"name": "Uttarakhand", "code": "UT"},
            {"name": "West Bengal", "code": "WB"},
        ]

        # Create state records
        for state_data in indian_states:
            state = State(
                id=uuid.uuid4(),
                name=state_data["name"],
                code=state_data["code"],
                country_id=india.id,
                is_active=True,
            )
            session.add(state)

        session.commit()
        print(f"Successfully seeded {len(indian_states)} Indian states")


def seed_us_states() -> None:
    """Seed US states as an example"""

    with Session(engine) as session:
        # Get USA's country ID
        usa = session.exec(select(Country).where(Country.code == "USA")).first()

        if not usa:
            print("USA not found in countries. Please seed countries first.")
            return

        # Check if states already exist for USA
        existing_states = session.exec(
            select(State).where(State.country_id == usa.id)
        ).first()
        if existing_states:
            print("US states already seeded. Skipping...")
            return

        # US states (sample - add more as needed)
        us_states = [
            {"name": "Alabama", "code": "AL"},
            {"name": "Alaska", "code": "AK"},
            {"name": "Arizona", "code": "AZ"},
            {"name": "Arkansas", "code": "AR"},
            {"name": "California", "code": "CA"},
            {"name": "Colorado", "code": "CO"},
            {"name": "Connecticut", "code": "CT"},
            {"name": "Delaware", "code": "DE"},
            {"name": "Florida", "code": "FL"},
            {"name": "Georgia", "code": "GA"},
            {"name": "Hawaii", "code": "HI"},
            {"name": "Idaho", "code": "ID"},
            {"name": "Illinois", "code": "IL"},
            {"name": "Indiana", "code": "IN"},
            {"name": "Iowa", "code": "IA"},
            {"name": "Kansas", "code": "KS"},
            {"name": "Kentucky", "code": "KY"},
            {"name": "Louisiana", "code": "LA"},
            {"name": "Maine", "code": "ME"},
            {"name": "Maryland", "code": "MD"},
            {"name": "Massachusetts", "code": "MA"},
            {"name": "Michigan", "code": "MI"},
            {"name": "Minnesota", "code": "MN"},
            {"name": "Mississippi", "code": "MS"},
            {"name": "Missouri", "code": "MO"},
            {"name": "Montana", "code": "MT"},
            {"name": "Nebraska", "code": "NE"},
            {"name": "Nevada", "code": "NV"},
            {"name": "New Hampshire", "code": "NH"},
            {"name": "New Jersey", "code": "NJ"},
            {"name": "New Mexico", "code": "NM"},
            {"name": "New York", "code": "NY"},
            {"name": "North Carolina", "code": "NC"},
            {"name": "North Dakota", "code": "ND"},
            {"name": "Ohio", "code": "OH"},
            {"name": "Oklahoma", "code": "OK"},
            {"name": "Oregon", "code": "OR"},
            {"name": "Pennsylvania", "code": "PA"},
            {"name": "Rhode Island", "code": "RI"},
            {"name": "South Carolina", "code": "SC"},
            {"name": "South Dakota", "code": "SD"},
            {"name": "Tennessee", "code": "TN"},
            {"name": "Texas", "code": "TX"},
            {"name": "Utah", "code": "UT"},
            {"name": "Vermont", "code": "VT"},
            {"name": "Virginia", "code": "VA"},
            {"name": "Washington", "code": "WA"},
            {"name": "West Virginia", "code": "WV"},
            {"name": "Wisconsin", "code": "WI"},
            {"name": "Wyoming", "code": "WY"},
        ]

        # Create state records
        for state_data in us_states:
            state = State(
                id=uuid.uuid4(),
                name=state_data["name"],
                code=state_data["code"],
                country_id=usa.id,
                is_active=True,
            )
            session.add(state)

        session.commit()
        print(f"Successfully seeded {len(us_states)} US states")


if __name__ == "__main__":
    print("Seeding states...")
    seed_indian_states()
    seed_us_states()
    print("State seeding complete!")
