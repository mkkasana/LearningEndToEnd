#!/usr/bin/env python3
"""Integration test script for Person Matching functionality."""

import sys
from datetime import date
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import os
os.chdir(backend_path)

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_religion import PersonReligion
from app.schemas.person.person_search import PersonSearchRequest
from app.services.person.person_matching_service import PersonMatchingService


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_result(description: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "✓" if passed else "✗"
    print(f"{status} {description}")
    if details:
        print(f"  {details}")
    print()


def get_test_metadata(session: Session) -> dict:
    """Get metadata IDs for testing."""
    from app.db_models.address.country import Country
    from app.db_models.address.district import District
    from app.db_models.address.state import State
    from app.db_models.person.gender import Gender
    from app.db_models.religion.religion import Religion
    from app.db_models.user import User

    # Get a test user
    user = session.exec(select(User).limit(1)).first()
    if not user:
        raise Exception("No users found in database. Please seed data first.")

    # Get gender
    gender = session.exec(select(Gender).limit(1)).first()
    if not gender:
        raise Exception("No genders found. Please seed data first.")

    # Get address metadata
    country = session.exec(select(Country).limit(1)).first()
    if not country:
        raise Exception("No countries found. Please seed data first.")

    state = session.exec(select(State).where(State.country_id == country.id).limit(1)).first()
    if not state:
        raise Exception("No states found. Please seed data first.")

    district = session.exec(
        select(District).where(District.state_id == state.id).limit(1)
    ).first()
    if not district:
        raise Exception("No districts found. Please seed data first.")

    # Get religion
    religion = session.exec(select(Religion).limit(1)).first()
    if not religion:
        raise Exception("No religions found. Please seed data first.")

    return {
        "user_id": user.id,
        "gender_id": gender.id,
        "country_id": country.id,
        "country_name": country.name,
        "state_id": state.id,
        "state_name": state.name,
        "district_id": district.id,
        "district_name": district.name,
        "religion_id": religion.id,
        "religion_name": religion.name,
    }


def create_test_person(
    session: Session,
    user_id,
    first_name: str,
    last_name: str,
    gender_id,
    metadata: dict,
) -> Person:
    """Create a test person with address and religion."""
    # Create person
    person = Person(
        user_id=None,  # Not linked to a user account
        created_by_user_id=user_id,
        is_primary=False,
        first_name=first_name,
        middle_name="Test",
        last_name=last_name,
        gender_id=gender_id,
        date_of_birth=date(1990, 1, 1),
    )
    session.add(person)
    session.commit()
    session.refresh(person)

    # Create address
    address = PersonAddress(
        person_id=person.id,
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        start_date=date(2020, 1, 1),
        is_current=True,
    )
    session.add(address)

    # Create religion
    religion = PersonReligion(
        person_id=person.id,
        religion_id=metadata["religion_id"],
    )
    session.add(religion)

    session.commit()
    return person


def test_exact_name_match(session: Session, metadata: dict):
    """Test finding person with exact name match."""
    print_section("Test 1: Exact Name Match")

    # Create a test person
    test_person = create_test_person(
        session,
        metadata["user_id"],
        "John",
        "Smith",
        metadata["gender_id"],
        metadata,
    )

    # Create search criteria
    search_criteria = PersonSearchRequest(
        first_name="John",
        last_name="Smith",
        middle_name="Test",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        religion_id=metadata["religion_id"],
        address_display=f"{metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}",
        religion_display=metadata["religion_name"],
    )

    # Search for matches
    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify results
    passed = len(results) > 0 and any(r.person_id == test_person.id for r in results)
    if passed:
        match = next(r for r in results if r.person_id == test_person.id)
        print_result(
            "Exact name match found",
            True,
            f"Match score: {match.match_score}% (Expected: 100%)",
        )
        assert match.match_score == 100.0, f"Expected 100% match, got {match.match_score}%"
    else:
        print_result("Exact name match found", False, "Person not found in results")

    # Cleanup
    session.delete(test_person)
    session.commit()

    return passed


def test_fuzzy_name_match(session: Session, metadata: dict):
    """Test finding person with fuzzy name match."""
    print_section("Test 2: Fuzzy Name Match")

    # Create a test person with slightly different name
    test_person = create_test_person(
        session,
        metadata["user_id"],
        "Jon",  # Similar to "John"
        "Smith",
        metadata["gender_id"],
        metadata,
    )

    # Search with slightly different name
    search_criteria = PersonSearchRequest(
        first_name="John",  # Searching for "John" but person is "Jon"
        last_name="Smith",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        religion_id=metadata["religion_id"],
        address_display=f"{metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}",
        religion_display=metadata["religion_name"],
    )

    # Search for matches
    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify results
    passed = len(results) > 0 and any(r.person_id == test_person.id for r in results)
    if passed:
        match = next(r for r in results if r.person_id == test_person.id)
        print_result(
            "Fuzzy name match found",
            True,
            f"Match score: {match.match_score}% (Expected: >90%)",
        )
        assert match.match_score > 90, f"Expected >90% match, got {match.match_score}%"
    else:
        print_result("Fuzzy name match found", False, "Person not found in results")

    # Cleanup
    session.delete(test_person)
    session.commit()

    return passed


def test_no_match_different_address(session: Session, metadata: dict):
    """Test that person with different address is not matched."""
    print_section("Test 3: No Match - Different Address")

    # Get a different district
    from app.db_models.address.district import District

    different_district = session.exec(
        select(District)
        .where(District.state_id == metadata["state_id"])
        .where(District.id != metadata["district_id"])
        .limit(1)
    ).first()

    if not different_district:
        print_result("Test skipped", False, "No alternative district available")
        return True

    # Create person with different address
    test_person = create_test_person(
        session,
        metadata["user_id"],
        "John",
        "Smith",
        metadata["gender_id"],
        metadata,
    )

    # Update address to different district
    address = session.exec(
        select(PersonAddress).where(PersonAddress.person_id == test_person.id)
    ).first()
    address.district_id = different_district.id
    session.commit()

    # Search with original district
    search_criteria = PersonSearchRequest(
        first_name="John",
        last_name="Smith",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],  # Different from person's district
        religion_id=metadata["religion_id"],
        address_display=f"{metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}",
        religion_display=metadata["religion_name"],
    )

    # Search for matches
    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify person is NOT in results
    passed = not any(r.person_id == test_person.id for r in results)
    print_result(
        "Person with different address excluded",
        passed,
        f"Found {len(results)} matches (person should not be included)",
    )

    # Cleanup
    session.delete(test_person)
    session.commit()

    return passed


def test_no_match_different_religion(session: Session, metadata: dict):
    """Test that person with different religion is not matched."""
    print_section("Test 4: No Match - Different Religion")

    # Get a different religion
    from app.db_models.religion.religion import Religion

    different_religion = session.exec(
        select(Religion).where(Religion.id != metadata["religion_id"]).limit(1)
    ).first()

    if not different_religion:
        print_result("Test skipped", False, "No alternative religion available")
        return True

    # Create person with different religion
    test_person = create_test_person(
        session,
        metadata["user_id"],
        "John",
        "Smith",
        metadata["gender_id"],
        metadata,
    )

    # Update religion
    religion = session.exec(
        select(PersonReligion).where(PersonReligion.person_id == test_person.id)
    ).first()
    religion.religion_id = different_religion.id
    session.commit()

    # Search with original religion
    search_criteria = PersonSearchRequest(
        first_name="John",
        last_name="Smith",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        religion_id=metadata["religion_id"],  # Different from person's religion
        address_display=f"{metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}",
        religion_display=metadata["religion_name"],
    )

    # Search for matches
    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify person is NOT in results
    passed = not any(r.person_id == test_person.id for r in results)
    print_result(
        "Person with different religion excluded",
        passed,
        f"Found {len(results)} matches (person should not be included)",
    )

    # Cleanup
    session.delete(test_person)
    session.commit()

    return passed


def test_threshold_filtering(session: Session, metadata: dict):
    """Test that low match scores are filtered out (below 60% threshold)."""
    print_section("Test 5: Match Score Threshold (60%)")

    # Create person with very different name
    test_person = create_test_person(
        session,
        metadata["user_id"],
        "Alexander",  # Very different from search name
        "Johnson",  # Very different from search name
        metadata["gender_id"],
        metadata,
    )

    # Search with completely different name
    search_criteria = PersonSearchRequest(
        first_name="Bob",
        last_name="Williams",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        religion_id=metadata["religion_id"],
        address_display=f"{metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}",
        religion_display=metadata["religion_name"],
    )

    # Search for matches
    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify person is NOT in results (score should be below 60%)
    passed = not any(r.person_id == test_person.id for r in results)
    print_result(
        "Low match score filtered out",
        passed,
        "Person with <60% match score correctly excluded",
    )

    # Cleanup
    session.delete(test_person)
    session.commit()

    return passed


def test_results_sorted_by_score(session: Session, metadata: dict):
    """Test that results are sorted by match score descending."""
    print_section("Test 6: Results Sorted by Match Score")

    # Create multiple test persons with varying name similarities
    person1 = create_test_person(
        session, metadata["user_id"], "John", "Smith", metadata["gender_id"], metadata
    )
    person2 = create_test_person(
        session, metadata["user_id"], "Jon", "Smith", metadata["gender_id"], metadata
    )
    person3 = create_test_person(
        session, metadata["user_id"], "Johnny", "Smith", metadata["gender_id"], metadata
    )

    # Search
    search_criteria = PersonSearchRequest(
        first_name="John",
        last_name="Smith",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        religion_id=metadata["religion_id"],
        address_display=f"{metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}",
        religion_display=metadata["religion_name"],
    )

    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify sorting
    scores = [r.match_score for r in results]
    passed = scores == sorted(scores, reverse=True)
    print_result(
        "Results sorted by match score",
        passed,
        f"Scores: {scores}",
    )

    # Cleanup
    session.delete(person1)
    session.delete(person2)
    session.delete(person3)
    session.commit()

    return passed


def test_limit_to_10_results(session: Session, metadata: dict):
    """Test that results are limited to top 10."""
    print_section("Test 7: Limit to Top 10 Results")

    # Create 15 test persons
    persons = []
    for i in range(15):
        person = create_test_person(
            session,
            metadata["user_id"],
            f"John{i}",
            "Smith",
            metadata["gender_id"],
            metadata,
        )
        persons.append(person)

    # Search
    search_criteria = PersonSearchRequest(
        first_name="John",
        last_name="Smith",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        religion_id=metadata["religion_id"],
        address_display=f"{metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}",
        religion_display=metadata["religion_name"],
    )

    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify limit
    passed = len(results) <= 10
    print_result(
        "Results limited to 10",
        passed,
        f"Returned {len(results)} results (max 10)",
    )

    # Cleanup
    for person in persons:
        session.delete(person)
    session.commit()

    return passed


def test_display_strings_used(session: Session, metadata: dict):
    """Test that display strings from request are used in results."""
    print_section("Test 8: Display Strings from Request")

    # Create test person
    test_person = create_test_person(
        session,
        metadata["user_id"],
        "John",
        "Smith",
        metadata["gender_id"],
        metadata,
    )

    # Custom display strings
    custom_address = "Custom Address Display"
    custom_religion = "Custom Religion Display"

    # Search
    search_criteria = PersonSearchRequest(
        first_name="John",
        last_name="Smith",
        gender_id=metadata["gender_id"],
        date_of_birth=date(1990, 1, 1),
        country_id=metadata["country_id"],
        state_id=metadata["state_id"],
        district_id=metadata["district_id"],
        religion_id=metadata["religion_id"],
        address_display=custom_address,
        religion_display=custom_religion,
    )

    service = PersonMatchingService(session)
    results = service.search_matching_persons(metadata["user_id"], search_criteria)

    # Verify display strings
    passed = False
    if results:
        match = results[0]
        passed = (
            match.address_display == custom_address
            and match.religion_display == custom_religion
        )
        print_result(
            "Display strings from request used",
            passed,
            f"Address: {match.address_display}, Religion: {match.religion_display}",
        )
    else:
        print_result("Display strings test", False, "No results found")

    # Cleanup
    session.delete(test_person)
    session.commit()

    return passed


def main():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("  Person Matching Service Integration Tests")
    print("=" * 70)

    # Create database connection
    session = Session(engine)

    try:
        # Get test metadata
        print_section("Setup")
        metadata = get_test_metadata(session)
        print(f"✓ Using test user: {metadata['user_id']}")
        print(f"✓ Using location: {metadata['country_name']}, {metadata['state_name']}, {metadata['district_name']}")
        print(f"✓ Using religion: {metadata['religion_name']}")

        # Run tests
        results = []
        results.append(test_exact_name_match(session, metadata))
        results.append(test_fuzzy_name_match(session, metadata))
        results.append(test_no_match_different_address(session, metadata))
        results.append(test_no_match_different_religion(session, metadata))
        results.append(test_threshold_filtering(session, metadata))
        results.append(test_results_sorted_by_score(session, metadata))
        results.append(test_limit_to_10_results(session, metadata))
        results.append(test_display_strings_used(session, metadata))

        # Summary
        passed = sum(results)
        total = len(results)

        print_section(f"Test Summary: {passed}/{total} Passed")

        if passed == total:
            print("✅ All tests passed!")
            return 0
        else:
            print(f"❌ {total - passed} test(s) failed")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
