"""Property-based tests for PersonService.

**Feature: contribution-stats**
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.services.person.person_service import PersonService


# Strategies for generating test data
uuid_strategy = st.uuids()
name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=("Cs",)))
date_strategy = st.dates(min_value=date(1900, 1, 1), max_value=date(2024, 12, 31))
address_line_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=("Cs",)))


class TestNameDisplayFormat:
    """Property-based tests for name display format.
    
    **Feature: contribution-stats, Property 2: Name Display Format**
    **Validates: Requirements 1.2**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        first_name=name_strategy,
        last_name=name_strategy,
    )
    def test_name_contains_first_and_last_name(
        self,
        db: Session,
        first_name: str,
        last_name: str,
    ) -> None:
        """Property 2: For any person with first_name and last_name,
        the contribution response should contain both names.
        """
        service = PersonService(db)
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()

        # Create mock person
        person = Person(
            id=person_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date(1980, 1, 1),
            date_of_death=None,
            gender_id=uuid.uuid4(),
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Mock dependencies
        with patch.object(
            service.person_repo, "get_by_creator", return_value=[person]
        ), patch(
            "app.services.person.person_service.ProfileViewTrackingService"
        ) as mock_view_service_class, patch(
            "app.services.person.person_service.PersonAddressRepository"
        ) as mock_address_repo_class:
            # Setup mocks
            mock_view_service = MagicMock()
            mock_view_service.get_total_views_bulk.return_value = {}
            mock_view_service_class.return_value = mock_view_service

            mock_address_repo = MagicMock()
            mock_address_repo.get_by_person_id.return_value = []
            mock_address_repo_class.return_value = mock_address_repo

            # Get contributions
            result = service.get_my_contributions(user_id)

            # Verify name fields are present
            assert len(result) == 1
            assert result[0]["first_name"] == first_name
            assert result[0]["last_name"] == last_name


class TestAddressFormatting:
    """Property-based tests for address formatting.
    
    **Feature: contribution-stats, Property 3: Address Formatting**
    **Validates: Requirements 1.3, 5.3**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        address_lines=st.lists(
            address_line_strategy,
            min_size=1,
            max_size=5,
        ),
    )
    def test_multiple_addresses_comma_separated(
        self,
        db: Session,
        address_lines: list[str],
    ) -> None:
        """Property 3: For any person with multiple addresses,
        the formatted address string should contain all address components
        separated by commas.
        """
        service = PersonService(db)
        person_id = uuid.uuid4()

        # Create mock addresses
        addresses = []
        for address_line in address_lines:
            addresses.append(
                PersonAddress(
                    id=uuid.uuid4(),
                    person_id=person_id,
                    country_id=uuid.uuid4(),
                    address_line=address_line,
                    start_date=date(2000, 1, 1),
                )
            )

        # Format addresses
        result = service._format_addresses(addresses)

        # Verify all address lines are present
        for address_line in address_lines:
            assert address_line in result

        # Verify comma separation (if more than one address)
        if len(address_lines) > 1:
            assert ", " in result


class TestDateRangeFormattingLiving:
    """Property-based tests for date range formatting (living persons).
    
    **Feature: contribution-stats, Property 4: Date Range Formatting for Living Persons**
    **Validates: Requirements 1.4**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        birth_date=date_strategy,
    )
    def test_living_person_shows_only_birth_year(
        self,
        db: Session,
        birth_date: date,
    ) -> None:
        """Property 4: For any person where date_of_death is NULL,
        the contribution response should include only the birth year.
        """
        service = PersonService(db)
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()

        # Create mock living person (no death date)
        person = Person(
            id=person_id,
            first_name="John",
            last_name="Doe",
            date_of_birth=birth_date,
            date_of_death=None,  # Living person
            gender_id=uuid.uuid4(),
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Mock dependencies
        with patch.object(
            service.person_repo, "get_by_creator", return_value=[person]
        ), patch(
            "app.services.person.person_service.ProfileViewTrackingService"
        ) as mock_view_service_class, patch(
            "app.services.person.person_service.PersonAddressRepository"
        ) as mock_address_repo_class:
            # Setup mocks
            mock_view_service = MagicMock()
            mock_view_service.get_total_views_bulk.return_value = {}
            mock_view_service_class.return_value = mock_view_service

            mock_address_repo = MagicMock()
            mock_address_repo.get_by_person_id.return_value = []
            mock_address_repo_class.return_value = mock_address_repo

            # Get contributions
            result = service.get_my_contributions(user_id)

            # Verify date fields
            assert len(result) == 1
            assert result[0]["date_of_birth"] == birth_date
            assert result[0]["date_of_death"] is None


class TestDateRangeFormattingDeceased:
    """Property-based tests for date range formatting (deceased persons).
    
    **Feature: contribution-stats, Property 5: Date Range Formatting for Deceased Persons**
    **Validates: Requirements 1.5**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        birth_date=date_strategy,
        death_date=date_strategy,
    )
    def test_deceased_person_shows_birth_and_death_year(
        self,
        db: Session,
        birth_date: date,
        death_date: date,
    ) -> None:
        """Property 5: For any person where date_of_death is NOT NULL,
        the contribution response should include both birth and death years.
        """
        # Ensure death date is after birth date
        if death_date < birth_date:
            birth_date, death_date = death_date, birth_date

        service = PersonService(db)
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()

        # Create mock deceased person
        person = Person(
            id=person_id,
            first_name="Jane",
            last_name="Smith",
            date_of_birth=birth_date,
            date_of_death=death_date,  # Deceased person
            gender_id=uuid.uuid4(),
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Mock dependencies
        with patch.object(
            service.person_repo, "get_by_creator", return_value=[person]
        ), patch(
            "app.services.person.person_service.ProfileViewTrackingService"
        ) as mock_view_service_class, patch(
            "app.services.person.person_service.PersonAddressRepository"
        ) as mock_address_repo_class:
            # Setup mocks
            mock_view_service = MagicMock()
            mock_view_service.get_total_views_bulk.return_value = {}
            mock_view_service_class.return_value = mock_view_service

            mock_address_repo = MagicMock()
            mock_address_repo.get_by_person_id.return_value = []
            mock_address_repo_class.return_value = mock_address_repo

            # Get contributions
            result = service.get_my_contributions(user_id)

            # Verify date fields
            assert len(result) == 1
            assert result[0]["date_of_birth"] == birth_date
            assert result[0]["date_of_death"] == death_date


class TestContributionsSorting:
    """Property-based tests for contributions sorting.
    
    **Feature: contribution-stats, Property 15: Contributions Sorted by View Count**
    **Validates: Requirements 5.5**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        view_counts=st.lists(
            st.integers(min_value=0, max_value=10000),
            min_size=2,
            max_size=10,
        ),
    )
    def test_contributions_sorted_by_view_count_descending(
        self,
        db: Session,
        view_counts: list[int],
    ) -> None:
        """Property 15: For any list of contributions,
        the results should be sorted by total_view_count in descending order
        (most viewed first).
        """
        service = PersonService(db)
        user_id = uuid.uuid4()

        # Create mock persons with different view counts
        persons = []
        view_count_map = {}

        for i, view_count in enumerate(view_counts):
            person_id = uuid.uuid4()
            person = Person(
                id=person_id,
                first_name=f"Person{i}",
                last_name=f"Test{i}",
                date_of_birth=date(1980, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                created_by_user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            persons.append(person)
            view_count_map[person_id] = view_count

        # Mock dependencies
        with patch.object(
            service.person_repo, "get_by_creator", return_value=persons
        ), patch(
            "app.services.person.person_service.ProfileViewTrackingService"
        ) as mock_view_service_class, patch(
            "app.services.person.person_service.PersonAddressRepository"
        ) as mock_address_repo_class:
            # Setup mocks
            mock_view_service = MagicMock()
            mock_view_service.get_total_views_bulk.return_value = view_count_map
            mock_view_service_class.return_value = mock_view_service

            mock_address_repo = MagicMock()
            mock_address_repo.get_by_person_id.return_value = []
            mock_address_repo_class.return_value = mock_address_repo

            # Get contributions
            result = service.get_my_contributions(user_id)

            # Verify sorting (descending order)
            assert len(result) == len(view_counts)

            # Check that each result has lower or equal view count than previous
            for i in range(len(result) - 1):
                assert result[i]["total_views"] >= result[i + 1]["total_views"]

            # Verify the highest view count is first
            expected_max = max(view_counts)
            assert result[0]["total_views"] == expected_max

            # Verify the lowest view count is last
            expected_min = min(view_counts)
            assert result[-1]["total_views"] == expected_min
