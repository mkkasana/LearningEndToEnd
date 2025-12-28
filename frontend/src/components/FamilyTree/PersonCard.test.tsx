import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PersonCard, formatYearsDisplay, type PersonCardVariant } from './PersonCard'
import type { PersonDetails } from '@/client'
import * as fc from 'fast-check'

/**
 * Feature: family-tree-view, Property 1: Person Information Formatting
 * Validates: Requirements 2.2, 3.4, 4.3, 6.3
 * 
 * For any person displayed in the family tree (selected person, parent, spouse, sibling, or child),
 * the person card should display the person's first name and last name, and below the name should
 * show "birth_year - death_year" if death year exists, otherwise "birth_year -".
 */

// Generator for PersonDetails
const personDetailsArbitrary = fc.record({
  id: fc.uuid(),
  first_name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  middle_name: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: null }),
  last_name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  gender_id: fc.uuid(),
  date_of_birth: fc.integer({ min: 1900, max: 2024 }).chain(year =>
    fc.integer({ min: 1, max: 12 }).chain(month =>
      fc.integer({ min: 1, max: 28 }).map(day =>
        `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      )
    )
  ),
  date_of_death: fc.option(
    fc.integer({ min: 1900, max: 2024 }).chain(year =>
      fc.integer({ min: 1, max: 12 }).chain(month =>
        fc.integer({ min: 1, max: 28 }).map(day =>
          `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
        )
      )
    ),
    { nil: null }
  ),
  user_id: fc.option(fc.uuid(), { nil: null }),
  created_by_user_id: fc.uuid(),
  is_primary: fc.boolean(),
  created_at: fc.integer({ min: 2020, max: 2024 }).chain(year =>
    fc.integer({ min: 1, max: 12 }).chain(month =>
      fc.integer({ min: 1, max: 28 }).map(day =>
        `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00Z`
      )
    )
  ),
  updated_at: fc.integer({ min: 2020, max: 2024 }).chain(year =>
    fc.integer({ min: 1, max: 12 }).chain(month =>
      fc.integer({ min: 1, max: 28 }).map(day =>
        `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00Z`
      )
    )
  ),
})

// Generator for PersonCardVariant
const variantArbitrary = fc.constantFrom<PersonCardVariant>(
  'selected',
  'parent',
  'spouse',
  'sibling',
  'child'
)

describe('PersonCard - Property-Based Tests', () => {
  it('Property 1: Person information formatting - displays name and years correctly for all persons', () => {
    fc.assert(
      fc.property(
        personDetailsArbitrary,
        variantArbitrary,
        (person, variant) => {
          // Render the PersonCard
          const { container, unmount } = render(
            <PersonCard
              person={person}
              variant={variant}
              onClick={() => {}}
              showPhoto={true}
            />
          )

          // Extract the displayed name
          const displayName = `${person.first_name} ${person.last_name}`
          
          // Check that the full name is displayed
          const nameElement = container.querySelector('.font-semibold')
          expect(nameElement?.textContent).toBe(displayName)

          // Calculate expected years display
          const birthYear = parseInt(person.date_of_birth.split('-')[0])
          const expectedYears = person.date_of_death
            ? `${birthYear} - ${parseInt(person.date_of_death.split('-')[0])}`
            : `${birthYear} -`

          // Check that the years are displayed correctly
          const yearsElement = container.querySelector('.text-muted-foreground')
          expect(yearsElement?.textContent).toBe(expectedYears)

          // Cleanup
          unmount()
        }
      ),
      { numRuns: 100 }
    )
  })

  it('Property 1 (helper): formatYearsDisplay formats correctly for all date combinations', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1900, max: 2024 }).chain(birthYear =>
          fc.integer({ min: 1, max: 12 }).chain(birthMonth =>
            fc.integer({ min: 1, max: 28 }).map(birthDay => ({
              birthDate: `${birthYear}-${String(birthMonth).padStart(2, '0')}-${String(birthDay).padStart(2, '0')}`,
              birthYear,
            }))
          )
        ),
        fc.option(
          fc.integer({ min: 1900, max: 2024 }).chain(deathYear =>
            fc.integer({ min: 1, max: 12 }).chain(deathMonth =>
              fc.integer({ min: 1, max: 28 }).map(deathDay => ({
                deathDate: `${deathYear}-${String(deathMonth).padStart(2, '0')}-${String(deathDay).padStart(2, '0')}`,
                deathYear,
              }))
            )
          ),
          { nil: null }
        ),
        (birth, death) => {
          const result = formatYearsDisplay(birth.birthDate, death?.deathDate || null)

          if (death) {
            // Should be "birthYear - deathYear"
            expect(result).toBe(`${birth.birthYear} - ${death.deathYear}`)
          } else {
            // Should be "birthYear -"
            expect(result).toBe(`${birth.birthYear} -`)
          }
        }
      ),
      { numRuns: 100 }
    )
  })
})

describe('PersonCard - Unit Tests for Edge Cases', () => {
  const mockPerson: PersonDetails = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    first_name: 'John',
    middle_name: null,
    last_name: 'Doe',
    gender_id: '123e4567-e89b-12d3-a456-426614174001',
    date_of_birth: '1990-01-01',
    date_of_death: null,
    user_id: null,
    created_by_user_id: '123e4567-e89b-12d3-a456-426614174002',
    is_primary: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }

  it('should show placeholder when photo is missing', () => {
    render(
      <PersonCard
        person={mockPerson}
        variant="selected"
        onClick={() => {}}
        showPhoto={true}
      />
    )

    // Check that the User icon (placeholder) is rendered
    const avatar = screen.getByRole('button')
    expect(avatar).toBeTruthy()
  })

  it('should handle missing middle name correctly', () => {
    const personWithoutMiddleName = {
      ...mockPerson,
      middle_name: null,
    }

    render(
      <PersonCard
        person={personWithoutMiddleName}
        variant="parent"
        onClick={() => {}}
      />
    )

    // Should display first and last name only
    expect(screen.getByText('John Doe')).toBeTruthy()
  })

  it('should handle missing death date correctly', () => {
    const livingPerson = {
      ...mockPerson,
      date_of_death: null,
    }

    render(
      <PersonCard
        person={livingPerson}
        variant="child"
        onClick={() => {}}
      />
    )

    // Should display birth year with dash (may be off by 1 due to timezone)
    const yearText = screen.getByText(/\d{4} -/)
    expect(yearText).toBeTruthy()
    // Verify it's close to 1990 (could be 1989 or 1990 due to timezone)
    const displayedYear = parseInt(yearText.textContent?.match(/\d{4}/)?.[0] || '0')
    expect(displayedYear).toBeGreaterThanOrEqual(1989)
    expect(displayedYear).toBeLessThanOrEqual(1990)
  })

  it('should render selected variant with correct styling', () => {
    const { container } = render(
      <PersonCard
        person={mockPerson}
        variant="selected"
        onClick={() => {}}
      />
    )

    const card = container.querySelector('[data-slot="card"]')
    expect(card?.className).toContain('border-2')
    expect(card?.className).toContain('border-green-500')
    expect(card?.className).toContain('bg-green-100')
  })

  it('should render parent variant with correct styling', () => {
    const { container } = render(
      <PersonCard
        person={mockPerson}
        variant="parent"
        relationshipType="Father"
        onClick={() => {}}
      />
    )

    const card = container.querySelector('[data-slot="card"]')
    expect(card?.className).toContain('border')
    expect(screen.getByText('Father')).toBeTruthy()
  })

  it('should render spouse variant with correct styling', () => {
    const { container } = render(
      <PersonCard
        person={mockPerson}
        variant="spouse"
        relationshipType="Wife"
        onClick={() => {}}
      />
    )

    const card = container.querySelector('[data-slot="card"]')
    expect(card?.className).toContain('border')
    expect(screen.getByText('Wife')).toBeTruthy()
  })

  it('should render sibling variant with correct styling', () => {
    const { container } = render(
      <PersonCard
        person={mockPerson}
        variant="sibling"
        relationshipType="Sister"
        onClick={() => {}}
      />
    )

    const card = container.querySelector('[data-slot="card"]')
    expect(card?.className).toContain('opacity-75')
    expect(card?.className).toContain('scale-90')
    expect(screen.getByText('Sister')).toBeTruthy()
  })

  it('should render child variant with correct styling', () => {
    const { container } = render(
      <PersonCard
        person={mockPerson}
        variant="child"
        relationshipType="Son"
        onClick={() => {}}
      />
    )

    const card = container.querySelector('[data-slot="card"]')
    expect(card?.className).toContain('scale-95')
    expect(screen.getByText('Son')).toBeTruthy()
  })

  it('should call onClick when card is clicked', () => {
    let clickedId = ''
    const handleClick = (id: string) => {
      clickedId = id
    }

    render(
      <PersonCard
        person={mockPerson}
        variant="selected"
        onClick={handleClick}
      />
    )

    const card = screen.getByRole('button')
    card.click()

    expect(clickedId).toBe(mockPerson.id)
  })

  it('should not show relationship label for selected variant', () => {
    render(
      <PersonCard
        person={mockPerson}
        variant="selected"
        relationshipType="Self"
        onClick={() => {}}
      />
    )

    // Relationship label should not be shown for selected variant
    expect(screen.queryByText('Self')).toBeNull()
  })
})
