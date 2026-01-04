#!/usr/bin/env python3
"""Seed script for users, persons, and family relationships.

This script seeds:
1. A test user with their primary person record
2. Family members (persons) created by that user
3. Relationships between family members
4. Demographic details (religion, address) for each person

Prerequisites:
- Genders must be seeded (seed_genders.py)
- Religions must be seeded (seed_religions.py)
- Address hierarchy must be seeded (countries, states, districts, etc.)
"""

import sys
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import get_password_hash
from app.db_models.user import User
from app.db_models.person import (
    Person,
    PersonRelationship,
    PersonReligion,
    PersonAddress,
    PersonLifeEvent,
)
from app.db_models.person.gender import Gender
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.db_models.address import Country, State, District, SubDistrict, Locality
from app.enums import RelationshipType
from app.schemas.person.life_event import LifeEventType


# Hardcoded UUIDs for consistent seeding
SEED_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
SEED_PERSON_IDS = {

    "dada_ji": uuid.UUID("82222222-2222-2222-2222-222222222202"),
    "dadi_ji": uuid.UUID("82222222-2222-2222-2222-222222222203"),

    "self": uuid.UUID("22222222-2222-2222-2222-222222222201"),
    "father": uuid.UUID("22222222-2222-2222-2222-222222222202"),
    "mother": uuid.UUID("22222222-2222-2222-2222-222222222203"),
    "spouse": uuid.UUID("22222222-2222-2222-2222-222222222204"),
    "son": uuid.UUID("22222222-2222-2222-2222-222222222205"),
    "daughter": uuid.UUID("22222222-2222-2222-2222-222222222206"),

    "m_self": uuid.UUID("32222222-2222-2222-2222-222222222201"),
    "m_father": uuid.UUID("32222222-2222-2222-2222-222222222202"),
    "m_mother": uuid.UUID("32222222-2222-2222-2222-222222222203"),
    "m_spouse": uuid.UUID("32222222-2222-2222-2222-222222222204"),
    "m_son": uuid.UUID("32222222-2222-2222-2222-222222222205"),
    "m_daughter": uuid.UUID("32222222-2222-2222-2222-222222222206"),
   
    "sib1_self": uuid.UUID("42222222-2222-2222-2222-222222222201"),
    "sib1_spouse": uuid.UUID("42222222-2222-2222-2222-222222222202"),
    "sib1_son": uuid.UUID("42222222-2222-2222-2222-222222222203"),
    
    "sib2_self": uuid.UUID("52222222-2222-2222-2222-222222222201"),
    "sib2_spouse": uuid.UUID("52222222-2222-2222-2222-222222222202"),

    "sib3_self": uuid.UUID("62222222-2222-2222-2222-222222222201"),
    "sib3_spouse": uuid.UUID("62222222-2222-2222-2222-222222222202"),

    "rati_self": uuid.UUID("92222222-2222-2222-2222-222222222201"),
    "rati_spouse": uuid.UUID("92222222-2222-2222-2222-222222222204"),
    "rati_son": uuid.UUID("92222222-2222-2222-2222-222222222205"),
    "rati_daughter": uuid.UUID("92222222-2222-2222-2222-222222222206"),
}

# Test user data
TEST_USER = {
    "id": SEED_USER_ID,
    "email": "testfamily@example.com",
    "password": "qweqweqwe",
    "full_name": "Self SelfM SelfL",
}

# Family members data
FAMILY_MEMBERS = [
    {
        "key": "dada_ji",
        "first_name": "dada_ji",
        "middle_name": None,
        "last_name": "dada_jiL",
        "gender_code": "MALE",
        "date_of_birth": date(1944, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "dadi_ji",
        "first_name": "dadi_ji",
        "middle_name": None,
        "last_name": "dadi_jiL",
        "gender_code": "FEMALE",
        "date_of_birth": date(1948, 1, 1),
        "is_primary": False,
        "user_id": None,
    },

    {
        "key": "self",
        "first_name": "self",
        "middle_name": "selfM",
        "last_name": "selfL",
        "gender_code": "MALE",
        "date_of_birth": date(1995, 1, 1),
        "is_primary": True,
        "user_id": SEED_USER_ID,
    },
    {
        "key": "father",
        "first_name": "father",
        "middle_name": None,
        "last_name": "fatherL",
        "gender_code": "MALE",
        "date_of_birth": date(1971, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "mother",
        "first_name": "mother",
        "middle_name": None,
        "last_name": "motherL",
        "gender_code": "FEMALE",
        "date_of_birth": date(1975, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "spouse",
        "first_name": "spouse",
        "middle_name": None,
        "last_name": "spouseL",
        "gender_code": "FEMALE",
        "date_of_birth": date(2000, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "son",
        "first_name": "son",
        "middle_name": None,
        "last_name": "sonL",
        "gender_code": "MALE",
        "date_of_birth": date(2025, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "daughter",
        "first_name": "daughter",
        "middle_name": None,
        "last_name": "daughterL",
        "gender_code": "FEMALE",
        "date_of_birth": date(2023, 1, 1),
        "is_primary": False,
        "user_id": None,
    },

    {
        "key": "m_self",
        "first_name": "m_self",
        "middle_name": None,
        "last_name": "m_selfL",
        "gender_code": "FEMALE",
        "date_of_birth": date(1995, 1, 1),
        "is_primary": True,
        "user_id": None,
    },
    {
        "key": "m_father",
        "first_name": "m_father",
        "middle_name": None,
        "last_name": "m_fatherL",
        "gender_code": "MALE",
        "date_of_birth": date(1971, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "m_mother",
        "first_name": "m_mother",
        "middle_name": None,
        "last_name": "m_motherL",
        "gender_code": "FEMALE",
        "date_of_birth": date(1975, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "m_spouse",
        "first_name": "m_spouse",
        "middle_name": None,
        "last_name": "m_spouseL",
        "gender_code": "FEMALE",
        "date_of_birth": date(2000, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "m_son",
        "first_name": "m_son",
        "middle_name": None,
        "last_name": "m_sonL",
        "gender_code": "MALE",
        "date_of_birth": date(2025, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "m_daughter",
        "first_name": "m_daughter",
        "middle_name": None,
        "last_name": "m_daughter",
        "gender_code": "FEMALE",
        "date_of_birth": date(2023, 1, 1),
        "is_primary": False,
        "user_id": None,
    },

    {
        "key": "sib1_self",
        "first_name": "sib1_self",
        "middle_name": None,
        "last_name": "sib1_selfL",
        "gender_code": "FEMALE",
        "date_of_birth": date(2001, 1, 1),
        "is_primary": True,
        "user_id": None,
    },
    {
        "key": "sib1_spouse",
        "first_name": "sib1_spouse",
        "middle_name": None,
        "last_name": "sib1_spouse",
        "gender_code": "MALE",
        "date_of_birth": date(1995, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "sib1_son",
        "first_name": "sib1_son",
        "middle_name": None,
        "last_name": "sib1_sonL",
        "gender_code": "MALE",
        "date_of_birth": date(2022, 1, 1),
        "is_primary": False,
        "user_id": None,
    },

    {
        "key": "sib2_self",
        "first_name": "sib2_self",
        "middle_name": None,
        "last_name": "sib2_selfL",
        "gender_code": "FEMALE",
        "date_of_birth": date(1997, 1, 1),
        "is_primary": True,
        "user_id": None,
    },
    {
        "key": "sib2_spouse",
        "first_name": "sib2_spouse",
        "middle_name": None,
        "last_name": "sib2_spouseL",
        "gender_code": "MALE",
        "date_of_birth": date(1998, 1, 1),
        "is_primary": False,
        "user_id": None,
    },

   {
        "key": "sib3_self",
        "first_name": "sib3_self",
        "middle_name": None,
        "last_name": "sib3_selfL",
        "gender_code": "FEMALE",
        "date_of_birth": date(2005, 1, 1),
        "is_primary": True,
        "user_id": None,
    },
    {
        "key": "sib3_spouse",
        "first_name": "sib3_spouse",
        "middle_name": None,
        "last_name": "sib3_spouseL",
        "gender_code": "MALE",
        "date_of_birth": date(2005, 1, 1),
        "is_primary": False,
        "user_id": None,
    },


    {
        "key": "rati_self",
        "first_name": "rati_self",
        "middle_name": None,
        "last_name": "rati_selfL",
        "gender_code": "MALE",
        "date_of_birth": date(1978, 1, 1),
        "is_primary": True,
        "user_id": None,
    },
    {
        "key": "rati_spouse",
        "first_name": "rati_spouse",
        "middle_name": None,
        "last_name": "rati_spouseL",
        "gender_code": "FEMALE",
        "date_of_birth": date(1981, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "rati_son",
        "first_name": "rati_son",
        "middle_name": None,
        "last_name": "rati_sonL",
        "gender_code": "MALE",
        "date_of_birth": date(1999, 1, 1),
        "is_primary": False,
        "user_id": None,
    },
    {
        "key": "rati_daughter",
        "first_name": "rati_daughter",
        "middle_name": None,
        "last_name": "rati_daughterL",
        "gender_code": "FEMALE",
        "date_of_birth": date(2005, 1, 1),
        "is_primary": False,
        "user_id": None,
    },

]

# Relationships: (from_person_key, to_person_key, relationship_type)
RELATIONSHIPS = [
    ("dada_ji", "dadi_ji", RelationshipType.SPOUSE),
    ("dadi_ji", "dada_ji", RelationshipType.SPOUSE),

    # Papa to Dada Dadi
    ("father", "dada_ji", RelationshipType.FATHER),
    ("dada_ji", "father", RelationshipType.SON),

    ("father", "dadi_ji", RelationshipType.MOTHER),
    ("dadi_ji", "father", RelationshipType.MOTHER),


    # Mami papa
    ("father", "mother", RelationshipType.SPOUSE),
    ("mother", "father", RelationshipType.SPOUSE),
    
    ("self", "father", RelationshipType.FATHER),
    ("father", "self", RelationshipType.SON),

    ("self", "mother", RelationshipType.MOTHER),
    ("mother", "self", RelationshipType.SON),

    ("self", "spouse", RelationshipType.SPOUSE),
    ("spouse", "self", RelationshipType.SPOUSE),

    # ("self", "son", RelationshipType.SON),
    ("self", "daughter", RelationshipType.DAUGHTER),
    ("daughter", "self", RelationshipType.FATHER),

    # self spouse sone
    ("spouse", "son", RelationshipType.SON),
    ("son", "spouse", RelationshipType.MOTHER),

    # M relation
    ("m_father", "m_mother", RelationshipType.SPOUSE),
    ("m_mother", "m_father", RelationshipType.SPOUSE),

    ("m_self", "m_father", RelationshipType.FATHER),
    ("m_father", "m_self", RelationshipType.DAUGHTER),

    ("m_self", "m_mother", RelationshipType.MOTHER),
    ("m_mother", "m_self", RelationshipType.DAUGHTER),

    ("m_self", "m_spouse", RelationshipType.SPOUSE),
    ("m_spouse", "m_self", RelationshipType.SPOUSE),

    ("m_self", "m_son", RelationshipType.SON),
    ("m_son", "m_self", RelationshipType.MOTHER),

    ("m_self", "m_daughter", RelationshipType.DAUGHTER),
    ("m_daughter", "m_self", RelationshipType.MOTHER),

    # sib1
    ("sib1_self", "father", RelationshipType.FATHER),
    ("father", "sib1_self", RelationshipType.DAUGHTER),

    ("sib1_self", "mother", RelationshipType.MOTHER),
    ("mother", "sib1_self", RelationshipType.DAUGHTER),

    ("sib1_self", "sib1_spouse", RelationshipType.SPOUSE),
    ("sib1_spouse", "sib1_self", RelationshipType.SPOUSE),

    ("sib1_self", "sib1_son", RelationshipType.SON),
    ("sib1_son", "sib1_self", RelationshipType.MOTHER),

    # sib2
    ("sib2_self", "father", RelationshipType.FATHER),
    ("father", "sib2_self", RelationshipType.DAUGHTER),

    ("sib2_self", "mother", RelationshipType.MOTHER),
    ("mother", "sib2_self", RelationshipType.DAUGHTER),

    ("sib2_self", "sib2_spouse", RelationshipType.SPOUSE),
    ("sib2_spouse", "sib2_self", RelationshipType.SPOUSE),

    # sib3
    ("sib3_self", "father", RelationshipType.FATHER),
    ("father", "sib3_self", RelationshipType.DAUGHTER),

    ("sib3_self", "mother", RelationshipType.MOTHER),
    ("mother", "sib3_self", RelationshipType.DAUGHTER),

    ("sib3_self", "sib3_spouse", RelationshipType.SPOUSE),
    ("sib3_spouse", "sib3_self", RelationshipType.SPOUSE),

    # Rati
    ("rati_self", "dada_ji", RelationshipType.FATHER),
    ("dada_ji", "rati_self", RelationshipType.SON),

    ("rati_self", "dadi_ji", RelationshipType.MOTHER),
    ("dadi_ji", "rati_self", RelationshipType.SON),

    ("rati_self", "rati_spouse", RelationshipType.SPOUSE),
    ("rati_spouse", "rati_self", RelationshipType.SPOUSE),

    ("rati_self", "rati_son", RelationshipType.SON),
    ("rati_son", "rati_self", RelationshipType.FATHER),

    ("rati_self", "rati_daughter", RelationshipType.DAUGHTER),
    ("rati_daughter", "rati_self", RelationshipType.FATHER),
]


def get_gender_id(session: Session, code: str) -> uuid.UUID | None:
    """Get gender ID by code."""
    gender = session.exec(select(Gender).where(Gender.code == code)).first()
    return gender.id if gender else None


def get_religion_ids(session: Session) -> dict:
    """Get Hinduism > Gurjar > Kasana IDs."""
    result = {}
    
    hinduism = session.exec(
        select(Religion).where(Religion.name == "Hinduism")
    ).first()
    if hinduism:
        result["religion_id"] = hinduism.id
        
        gurjar = session.exec(
            select(ReligionCategory)
            .where(ReligionCategory.name == "Gurjar")
            .where(ReligionCategory.religion_id == hinduism.id)
        ).first()
        if gurjar:
            result["category_id"] = gurjar.id
            
            kasana = session.exec(
                select(ReligionSubCategory)
                .where(ReligionSubCategory.name == "Kasana")
                .where(ReligionSubCategory.category_id == gurjar.id)
            ).first()
            if kasana:
                result["sub_category_id"] = kasana.id
    
    return result


def get_address_ids(session: Session) -> dict:
    """Get India > Rajasthan > Dausa > Sikrai > Bhojpura IDs."""
    result = {}
    
    india = session.exec(select(Country).where(Country.code == "IND")).first()
    if india:
        result["country_id"] = india.id
        
        rajasthan = session.exec(
            select(State)
            .where(State.code == "RJ")
            .where(State.country_id == india.id)
        ).first()
        if rajasthan:
            result["state_id"] = rajasthan.id
            
            dausa = session.exec(
                select(District)
                .where(District.name == "Dausa")
                .where(District.state_id == rajasthan.id)
            ).first()
            if dausa:
                result["district_id"] = dausa.id
                
                sikrai = session.exec(
                    select(SubDistrict)
                    .where(SubDistrict.name == "Sikrai")
                    .where(SubDistrict.district_id == dausa.id)
                ).first()
                if sikrai:
                    result["sub_district_id"] = sikrai.id
                    
                    bhojpura = session.exec(
                        select(Locality)
                        .where(Locality.name == "Bhojpura")
                        .where(Locality.sub_district_id == sikrai.id)
                    ).first()
                    if bhojpura:
                        result["locality_id"] = bhojpura.id
    
    return result


def add_default_address_for_person(
    session: Session,
    person_id: uuid.UUID,
    start_date: date | None = None,
    is_current: bool = True,
) -> PersonAddress | None:
    """
    Add default address (India > Rajasthan > Dausa > Sikrai > Bhojpura) for a person.
    
    Args:
        session: Database session
        person_id: UUID of the person to add address for
        start_date: Start date for the address (defaults to today)
        is_current: Whether this is the current address (defaults to True)
    
    Returns:
        PersonAddress if created successfully, None otherwise
    """
    # Check if person already has an address
    existing = session.exec(
        select(PersonAddress).where(PersonAddress.person_id == person_id)
    ).first()
    if existing:
        print(f"  ⊘ Person {person_id} already has an address")
        return existing
    
    # Get address hierarchy IDs
    address_ids = get_address_ids(session)
    
    if not address_ids.get("country_id"):
        print("  ❌ India not found. Please seed countries first.")
        return None
    
    # Use today's date if not provided
    if start_date is None:
        start_date = date.today()
    
    person_address = PersonAddress(
        person_id=person_id,
        country_id=address_ids.get("country_id"),
        state_id=address_ids.get("state_id"),
        district_id=address_ids.get("district_id"),
        sub_district_id=address_ids.get("sub_district_id"),
        locality_id=address_ids.get("locality_id"),
        start_date=start_date,
        is_current=is_current,
    )
    session.add(person_address)
    session.flush()
    print(f"  ✓ Added default address for person {person_id}")
    return person_address


def add_default_religion_for_person(
    session: Session,
    person_id: uuid.UUID,
) -> PersonReligion | None:
    """
    Add default religion (Hinduism > Gurjar > Kasana) for a person.
    
    Args:
        session: Database session
        person_id: UUID of the person to add religion for
    
    Returns:
        PersonReligion if created successfully, None otherwise
    """
    # Check if person already has religion details
    existing = session.exec(
        select(PersonReligion).where(PersonReligion.person_id == person_id)
    ).first()
    if existing:
        print(f"  ⊘ Person {person_id} already has religion details")
        return existing
    
    # Get religion hierarchy IDs
    religion_ids = get_religion_ids(session)
    
    if not religion_ids.get("religion_id"):
        print("  ❌ Hinduism not found. Please seed religions first.")
        return None
    
    person_religion = PersonReligion(
        person_id=person_id,
        religion_id=religion_ids.get("religion_id"),
        religion_category_id=religion_ids.get("category_id"),
        religion_sub_category_id=religion_ids.get("sub_category_id"),
    )
    session.add(person_religion)
    session.flush()
    print(f"  ✓ Added default religion for person {person_id}")
    return person_religion


def add_default_demographics_for_person(
    session: Session,
    person_id: uuid.UUID,
    address_start_date: date | None = None,
) -> tuple[PersonAddress | None, PersonReligion | None]:
    """
    Add both default address and religion for a person.
    
    This is a convenience function that adds:
    - Address: India > Rajasthan > Dausa > Sikrai > Bhojpura
    - Religion: Hinduism > Gurjar > Kasana
    
    Args:
        session: Database session
        person_id: UUID of the person to add demographics for
        address_start_date: Start date for the address (defaults to today)
    
    Returns:
        Tuple of (PersonAddress, PersonReligion) - either can be None if failed
    """
    print(f"Adding default demographics for person {person_id}...")
    
    address = add_default_address_for_person(
        session, person_id, start_date=address_start_date
    )
    religion = add_default_religion_for_person(session, person_id)
    
    return address, religion


def seed_test_user(session: Session) -> User | None:
    """Seed the test user."""
    existing = session.exec(select(User).where(User.id == SEED_USER_ID)).first()
    if existing:
        print("✓ Test user already exists")
        return existing
    
    print("Creating test user...")
    user = User(
        id=TEST_USER["id"],
        email=TEST_USER["email"],
        hashed_password=get_password_hash(TEST_USER["password"]),
        full_name=TEST_USER["full_name"],
        is_active=True,
    )
    session.add(user)
    session.flush()
    print(f"  ✓ Created user: {user.email}")
    return user


def seed_persons(session: Session, user: User) -> dict[str, Person]:
    """Seed family members as persons."""
    persons = {}
    
    # Check if persons already exist
    existing = session.exec(
        select(Person).where(Person.id == SEED_PERSON_IDS["self"])
    ).first()
    if existing:
        print("✓ Persons already seeded")
        # Load existing persons
        for key, person_id in SEED_PERSON_IDS.items():
            person = session.exec(select(Person).where(Person.id == person_id)).first()
            if person:
                persons[key] = person
        return persons
    
    print("Creating family members...")
    
    for member in FAMILY_MEMBERS:
        gender_id = get_gender_id(session, member["gender_code"])
        if not gender_id:
            print(f"  ❌ Gender {member['gender_code']} not found. Skipping {member['first_name']}")
            continue
        
        person = Person(
            id=SEED_PERSON_IDS[member["key"]],
            user_id=member["user_id"],
            created_by_user_id=user.id,
            is_primary=member["is_primary"],
            first_name=member["first_name"],
            middle_name=member["middle_name"],
            last_name=member["last_name"],
            gender_id=gender_id,
            date_of_birth=member["date_of_birth"],
        )
        session.add(person)
        persons[member["key"]] = person
        print(f"  ✓ Created person: {member['first_name']} {member['last_name']} ({member['key']})")
    
    session.flush()
    return persons


def seed_person_religions(session: Session, persons: dict[str, Person]) -> None:
    """Seed religion details for all persons using the default religion."""
    # Check if already seeded
    existing = session.exec(
        select(PersonReligion).where(PersonReligion.person_id == SEED_PERSON_IDS["self"])
    ).first()
    if existing:
        print("✓ Person religions already seeded")
        return
    
    print("Adding religion details for family members...")
    
    for key, person in persons.items():
        add_default_religion_for_person(session, person.id)
    
    print("✅ Person religions seeded!")


def seed_person_addresses(session: Session, persons: dict[str, Person]) -> None:
    """Seed address details for all persons using the default address."""
    # Check if already seeded
    existing = session.exec(
        select(PersonAddress).where(PersonAddress.person_id == SEED_PERSON_IDS["self"])
    ).first()
    if existing:
        print("✓ Person addresses already seeded")
        return
    
    print("Adding address details for family members...")
    
    for key, person in persons.items():
        add_default_address_for_person(
            session, person.id, start_date=person.date_of_birth
        )
    
    print("✅ Person addresses seeded!")


def seed_relationships(session: Session, persons: dict[str, Person]) -> None:
    """Seed relationships between family members."""
    # Check if already seeded
    existing = session.exec(
        select(PersonRelationship).where(
            PersonRelationship.person_id == SEED_PERSON_IDS["self"]
        )
    ).first()
    if existing:
        print("✓ Relationships already seeded")
        return
    
    print("Creating family relationships...")
    
    for from_key, to_key, rel_type in RELATIONSHIPS:
        from_person = persons.get(from_key)
        to_person = persons.get(to_key)
        
        if not from_person or not to_person:
            print(f"  ❌ Missing person for relationship: {from_key} -> {to_key}")
            continue
        
        relationship = PersonRelationship(
            person_id=from_person.id,
            related_person_id=to_person.id,
            relationship_type=rel_type,
            is_active=True,
        )
        session.add(relationship)
        print(f"  ✓ {from_person.first_name} -> {to_person.first_name} ({rel_type.label})")
    
    session.flush()
    print("✅ Relationships seeded!")


def seed_life_events(session: Session, persons: dict[str, Person]) -> None:
    """Seed life events for family members."""
    # Check if already seeded
    existing = session.exec(
        select(PersonLifeEvent).where(
            PersonLifeEvent.person_id == SEED_PERSON_IDS["self"]
        )
    ).first()
    if existing:
        print("✓ Life events already seeded")
        return
    
    print("Creating life events...")
    
    # Life events for "self" person
    self_person = persons.get("self")
    if self_person:
        events = [
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=self_person.id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                description="Born in Sikrai village",
                event_year=1995,
                event_month=3,
                event_date=15,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=self_person.id,
                event_type=LifeEventType.EDUCATION,
                title="Started School",
                description="Joined primary school",
                event_year=2001,
                event_month=7,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=self_person.id,
                event_type=LifeEventType.ACHIEVEMENT,
                title="Graduated High School",
                description="Completed 12th grade",
                event_year=2013,
                event_month=5,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=self_person.id,
                event_type=LifeEventType.EDUCATION,
                title="College Admission",
                description="Admitted to engineering college",
                event_year=2013,
                event_month=8,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=self_person.id,
                event_type=LifeEventType.ACHIEVEMENT,
                title="Graduated College",
                description="Completed B.Tech degree",
                event_year=2017,
                event_month=6,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=self_person.id,
                event_type=LifeEventType.CAREER,
                title="First Job",
                description="Started working as software engineer",
                event_year=2017,
                event_month=8,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=self_person.id,
                event_type=LifeEventType.MARRIAGE,
                title="Wedding",
                description="Married to spouse",
                event_year=2020,
                event_month=2,
                event_date=14,
            ),
        ]
        for event in events:
            session.add(event)
        print(f"  ✓ Added {len(events)} life events for {self_person.first_name}")
    
    # Life events for father
    father_person = persons.get("father")
    if father_person:
        events = [
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=father_person.id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                event_year=1970,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=father_person.id,
                event_type=LifeEventType.MARRIAGE,
                title="Wedding",
                description="Married to mother",
                event_year=1994,
                event_month=11,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=father_person.id,
                event_type=LifeEventType.CAREER,
                title="Started Business",
                description="Started own business",
                event_year=1995,
            ),
        ]
        for event in events:
            session.add(event)
        print(f"  ✓ Added {len(events)} life events for {father_person.first_name}")
    
    # Life events for mother
    mother_person = persons.get("mother")
    if mother_person:
        events = [
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=mother_person.id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                event_year=1975,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=mother_person.id,
                event_type=LifeEventType.MARRIAGE,
                title="Wedding",
                description="Married to father",
                event_year=1994,
                event_month=11,
            ),
        ]
        for event in events:
            session.add(event)
        print(f"  ✓ Added {len(events)} life events for {mother_person.first_name}")
    
    # Life events for spouse
    spouse_person = persons.get("spouse")
    if spouse_person:
        events = [
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=spouse_person.id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                event_year=1996,
                event_month=8,
                event_date=20,
            ),
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=spouse_person.id,
                event_type=LifeEventType.MARRIAGE,
                title="Wedding",
                description="Married to self",
                event_year=2020,
                event_month=2,
                event_date=14,
            ),
        ]
        for event in events:
            session.add(event)
        print(f"  ✓ Added {len(events)} life events for {spouse_person.first_name}")
    
    # Life events for son
    son_person = persons.get("son")
    if son_person:
        events = [
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=son_person.id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                description="Born at hospital",
                event_year=2021,
                event_month=5,
                event_date=10,
            ),
        ]
        for event in events:
            session.add(event)
        print(f"  ✓ Added {len(events)} life events for {son_person.first_name}")
    
    # Life events for daughter
    daughter_person = persons.get("daughter")
    if daughter_person:
        events = [
            PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=daughter_person.id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                description="Born at hospital",
                event_year=2023,
                event_month=9,
                event_date=25,
            ),
        ]
        for event in events:
            session.add(event)
        print(f"  ✓ Added {len(events)} life events for {daughter_person.first_name}")
    
    session.flush()
    print("✅ Life events seeded!")


def seed_family() -> None:
    """Seed complete family data: user, persons, demographics, and relationships."""
    print("=" * 60)
    print("Starting family seeding...")
    print("=" * 60)
    print()
    
    with Session(engine) as session:
        # 1. Create test user
        user = seed_test_user(session)
        if not user:
            print("❌ Failed to create user")
            return
        print()
        
        # 2. Create family members (persons)
        persons = seed_persons(session, user)
        if not persons:
            print("❌ Failed to create persons")
            return
        print()
        
        # 3. Add religion details
        seed_person_religions(session, persons)
        print()
        
        # 4. Add address details
        seed_person_addresses(session, persons)
        print()
        
        # 5. Create relationships
        seed_relationships(session, persons)
        print()
        
        # 6. Add life events
        seed_life_events(session, persons)
        print()
        
        # Commit all changes
        session.commit()
    
    print("=" * 60)
    print("✅ Family seeding completed!")
    print()
    print("Test User Credentials:")
    print(f"  Email: {TEST_USER['email']}")
    print(f"  Password: {TEST_USER['password']}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        seed_family()
    except Exception as e:
        print(f"❌ Error seeding family: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
