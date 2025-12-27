#!/usr/bin/env python3
"""
Migration script for bidirectional relationships.

This script identifies all relationships that lack an inverse relationship
and creates the missing inverse relationships with the correct type.

Usage:
    python scripts/migrate_bidirectional_relationships.py [--dry-run]

Options:
    --dry-run    Report what would be created without creating (default: False)
"""

import argparse
import logging
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.utils.relationship_helper import RelationshipTypeHelper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("migration_bidirectional_relationships.log"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Run the migration."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Migrate existing relationships to bidirectional"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be created without creating",
    )
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("Starting bidirectional relationship migration")
    logger.info(f"Dry run mode: {args.dry_run}")
    logger.info("=" * 80)
    logger.info("")

    try:
        with Session(engine) as session:
            migrate_relationships(session, dry_run=args.dry_run)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ Migration completed successfully!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        sys.exit(1)


def migrate_relationships(session: Session, dry_run: bool = False) -> None:
    """
    Migrate existing relationships to bidirectional.

    Args:
        session: Database session
        dry_run: If True, report what would be created without creating
    """
    # Initialize repository
    relationship_repo = PersonRelationshipRepository(session)

    # Get gender mapping
    logger.info("Loading gender mapping...")
    gender_mapping = RelationshipTypeHelper.get_gender_mapping(session)
    logger.info(f"Loaded {len(gender_mapping)} gender entries")
    logger.info("")

    # Query all existing relationships
    logger.info("Querying all existing relationships...")
    statement = select(PersonRelationship).order_by(PersonRelationship.created_at)
    all_relationships = session.exec(statement).all()
    logger.info(f"Found {len(all_relationships)} total relationships")
    logger.info("")

    # Track statistics
    created_count = 0
    skipped_count = 0
    error_count = 0
    missing_gender_count = 0

    # Process each relationship
    logger.info("Processing relationships...")
    for idx, relationship in enumerate(all_relationships, 1):
        # Log progress every 100 relationships
        if idx % 100 == 0:
            logger.info(
                f"Progress: {idx}/{len(all_relationships)} relationships processed "
                f"(created: {created_count}, skipped: {skipped_count}, "
                f"errors: {error_count}, missing_gender: {missing_gender_count})"
            )

        try:
            # Check if inverse exists (idempotency check)
            inverse = relationship_repo.find_inverse_including_inactive(
                person_id=relationship.person_id,
                related_person_id=relationship.related_person_id,
            )

            if inverse:
                # Inverse already exists, skip
                skipped_count += 1
                logger.debug(
                    f"Skipping relationship {relationship.id}: inverse already exists"
                )
                continue

            # Fetch person and related_person to get gender information
            person = session.get(Person, relationship.person_id)
            related_person = session.get(Person, relationship.related_person_id)

            if not person or not related_person:
                logger.warning(
                    f"Relationship {relationship.id}: Person not found "
                    f"(person_id={relationship.person_id}, "
                    f"related_person_id={relationship.related_person_id})"
                )
                error_count += 1
                continue

            # Check if both persons have gender information
            if not person.gender_id or not related_person.gender_id:
                logger.warning(
                    f"Relationship {relationship.id}: Missing gender information "
                    f"(person.gender_id={person.gender_id}, "
                    f"related_person.gender_id={related_person.gender_id}). "
                    f"Cannot create inverse."
                )
                missing_gender_count += 1
                continue

            # Determine inverse relationship type
            inverse_type = RelationshipTypeHelper.get_inverse_type(
                relationship_type=relationship.relationship_type,
                person_gender_id=person.gender_id,
                related_person_gender_id=related_person.gender_id,
                gender_mapping=gender_mapping,
            )

            if not inverse_type:
                logger.warning(
                    f"Relationship {relationship.id}: Could not determine inverse type "
                    f"for relationship_type={relationship.relationship_type}"
                )
                error_count += 1
                continue

            # Create inverse relationship
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would create inverse: "
                    f"person_id={relationship.related_person_id}, "
                    f"related_person_id={relationship.person_id}, "
                    f"type={inverse_type}, "
                    f"is_active={relationship.is_active}"
                )
            else:
                inverse_relationship = PersonRelationship(
                    person_id=relationship.related_person_id,
                    related_person_id=relationship.person_id,
                    relationship_type=inverse_type,
                    is_active=relationship.is_active,
                    start_date=relationship.start_date,
                    end_date=relationship.end_date,
                )
                session.add(inverse_relationship)
                logger.debug(
                    f"Created inverse for relationship {relationship.id}: "
                    f"type={inverse_type}"
                )

            created_count += 1

        except Exception as e:
            logger.error(
                f"Error processing relationship {relationship.id}: {e}", exc_info=True
            )
            error_count += 1
            continue

    # Commit changes if not dry run
    if not dry_run and created_count > 0:
        logger.info("")
        logger.info("Committing changes to database...")
        session.commit()
        logger.info("Changes committed successfully")

    # Print summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("Migration Summary")
    logger.info("=" * 80)
    logger.info(f"Total relationships processed: {len(all_relationships)}")
    logger.info(f"Inverse relationships created: {created_count}")
    logger.info(f"Relationships skipped (already have inverse): {skipped_count}")
    logger.info(f"Relationships with missing gender: {missing_gender_count}")
    logger.info(f"Errors encountered: {error_count}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
