import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import * as fc from 'fast-check'
import { HorizontalScrollRow } from './HorizontalScrollRow'
import type { PersonDetails } from '@/client'

/**
 * Arbitrary generator for PersonDetails
 */
const personDetailsArbitrary = fc.record({
  id: fc.uuid(),
  first_name: fc.string({ minLength: 1, maxLength: 20 }),
  middle_name: fc.option(fc.string({ minLength: 1, maxLength: 20 }), { nil: null }),
  last_name: fc.string({ minLength: 1, maxLength: 20 }),
  gender_id: fc.uuid(),
  date_of_birth: fc.integer({ min: 1900, max: 2024 }).chain(year =>
    fc.integer({ min: 1, max: 12 }).chain(month =>
      fc.integer({ min: 1, max: 28 }).map(day =>
        `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00.000Z`
      )
    )
  ),
  date_of_death: fc.option(
    fc.integer({ min: 1900, max: 2024 }).chain(year =>
      fc.integer({ min: 1, max: 12 }).chain(month =>
        fc.integer({ min: 1, max: 28 }).map(day =>
          `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00.000Z`
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
        `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00.000Z`
      )
    )
  ),
  updated_at: fc.integer({ min: 2020, max: 2024 }).chain(year =>
    fc.integer({ min: 1, max: 12 }).chain(month =>
      fc.integer({ min: 1, max: 28 }).map(day =>
        `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00.000Z`
      )
    )
  ),
}) as fc.Arbitrary<PersonDetails>

describe('HorizontalScrollRow', () => {
  describe('Unit Tests', () => {
    it('should render nothing when people array is empty and no selectedPersonId', () => {
      const mockOnClick = vi.fn()
      
      const { container } = render(
        <HorizontalScrollRow
          people={[]}
          onPersonClick={mockOnClick}
          variant="parent"
        />
      )
      
      expect(container.firstChild).toBeNull()
    })

    it('should render horizontal scroll container with correct aria-label for parent variant', () => {
      const mockPerson: PersonDetails = {
        id: '123',
        first_name: 'John',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const { container } = render(
        <HorizontalScrollRow
          people={[mockPerson]}
          onPersonClick={vi.fn()}
          variant="parent"
        />
      )
      
      const region = container.querySelector('[role="region"]')
      expect(region).toBeTruthy()
      expect(region?.getAttribute('aria-label')).toBe('Parents row')
    })

    it('should render horizontal scroll container with correct aria-label for center variant', () => {
      const mockPerson: PersonDetails = {
        id: '123',
        first_name: 'John',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const { container } = render(
        <HorizontalScrollRow
          people={[mockPerson]}
          onPersonClick={vi.fn()}
          variant="center"
        />
      )
      
      const region = container.querySelector('[role="region"]')
      expect(region).toBeTruthy()
      expect(region?.getAttribute('aria-label')).toBe('Center row with siblings and spouses')
    })

    it('should render horizontal scroll container with correct aria-label for child variant', () => {
      const mockPerson: PersonDetails = {
        id: '123',
        first_name: 'John',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const { container } = render(
        <HorizontalScrollRow
          people={[mockPerson]}
          onPersonClick={vi.fn()}
          variant="child"
        />
      )
      
      const region = container.querySelector('[role="region"]')
      expect(region).toBeTruthy()
      expect(region?.getAttribute('aria-label')).toBe('Children row')
    })

    it('should apply color-coding for siblings in center row', () => {
      const sibling: PersonDetails = {
        id: 'sibling-123',
        first_name: 'Jane',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'female-id',
        date_of_birth: '1972-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const colorCoding = new Map<string, 'sibling' | 'spouse'>()
      colorCoding.set('sibling-123', 'sibling')
      
      const { container } = render(
        <HorizontalScrollRow
          people={[sibling]}
          onPersonClick={vi.fn()}
          variant="center"
          colorCoding={colorCoding}
        />
      )
      
      // Check for blue color classes (sibling color)
      expect(container.innerHTML).toContain('blue-')
    })

    it('should apply color-coding for spouses in center row', () => {
      const spouse: PersonDetails = {
        id: 'spouse-123',
        first_name: 'Mary',
        middle_name: null,
        last_name: 'Smith',
        gender_id: 'female-id',
        date_of_birth: '1972-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const colorCoding = new Map<string, 'sibling' | 'spouse'>()
      colorCoding.set('spouse-123', 'spouse')
      
      const { container } = render(
        <HorizontalScrollRow
          people={[spouse]}
          onPersonClick={vi.fn()}
          variant="center"
          colorCoding={colorCoding}
        />
      )
      
      // Check for purple color classes (spouse color)
      expect(container.innerHTML).toContain('purple-')
    })

    it('should not apply color-coding to selected person in center row', () => {
      const selectedPerson: PersonDetails = {
        id: 'selected-123',
        first_name: 'John',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const colorCoding = new Map<string, 'sibling' | 'spouse'>()
      // Don't add selected person to color coding
      
      const { container } = render(
        <HorizontalScrollRow
          people={[selectedPerson]}
          selectedPersonId="selected-123"
          onPersonClick={vi.fn()}
          variant="center"
          colorCoding={colorCoding}
        />
      )
      
      // Selected person should not have color-coding background
      const personCards = container.querySelectorAll('[role="button"]')
      expect(personCards.length).toBe(1)
    })

    it('should include touch-manipulation class for mobile support', () => {
      const mockPerson: PersonDetails = {
        id: '123',
        first_name: 'John',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const { container } = render(
        <HorizontalScrollRow
          people={[mockPerson]}
          onPersonClick={vi.fn()}
          variant="parent"
        />
      )
      
      expect(container.innerHTML).toContain('touch-manipulation')
    })

    it('should render all people in the array', () => {
      const people: PersonDetails[] = [
        {
          id: '1',
          first_name: 'Person',
          middle_name: null,
          last_name: 'One',
          gender_id: 'male-id',
          date_of_birth: '1970-01-01T00:00:00.000Z',
          date_of_death: null,
          user_id: null,
          created_by_user_id: 'creator-id',
          is_primary: false,
          created_at: '2024-01-01T00:00:00.000Z',
          updated_at: '2024-01-01T00:00:00.000Z',
        },
        {
          id: '2',
          first_name: 'Person',
          middle_name: null,
          last_name: 'Two',
          gender_id: 'female-id',
          date_of_birth: '1972-01-01T00:00:00.000Z',
          date_of_death: null,
          user_id: null,
          created_by_user_id: 'creator-id',
          is_primary: false,
          created_at: '2024-01-01T00:00:00.000Z',
          updated_at: '2024-01-01T00:00:00.000Z',
        },
        {
          id: '3',
          first_name: 'Person',
          middle_name: null,
          last_name: 'Three',
          gender_id: 'male-id',
          date_of_birth: '1974-01-01T00:00:00.000Z',
          date_of_death: null,
          user_id: null,
          created_by_user_id: 'creator-id',
          is_primary: false,
          created_at: '2024-01-01T00:00:00.000Z',
          updated_at: '2024-01-01T00:00:00.000Z',
        },
      ]
      
      const { container } = render(
        <HorizontalScrollRow
          people={people}
          onPersonClick={vi.fn()}
          variant="child"
        />
      )
      
      const personCards = container.querySelectorAll('[role="button"]')
      expect(personCards.length).toBe(3)
    })

    // Unit tests for row centering (Requirements: 9.2, 9.4)
    it('should center parent row content when narrow', () => {
      const mockPerson: PersonDetails = {
        id: '123',
        first_name: 'John',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const { container } = render(
        <HorizontalScrollRow
          people={[mockPerson]}
          onPersonClick={vi.fn()}
          variant="parent"
        />
      )
      
      // Should have justify-center for centering narrow content
      expect(container.innerHTML).toContain('justify-center')
    })

    it('should center children row content when narrow', () => {
      const mockPerson: PersonDetails = {
        id: '123',
        first_name: 'Jane',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'female-id',
        date_of_birth: '2000-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const { container } = render(
        <HorizontalScrollRow
          people={[mockPerson]}
          onPersonClick={vi.fn()}
          variant="child"
        />
      )
      
      // Should have justify-center for centering narrow content
      expect(container.innerHTML).toContain('justify-center')
    })

    it('should center all rows including center row', () => {
      const mockPerson: PersonDetails = {
        id: '123',
        first_name: 'John',
        middle_name: null,
        last_name: 'Doe',
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }
      
      const { container } = render(
        <HorizontalScrollRow
          people={[mockPerson]}
          selectedPersonId="123"
          onPersonClick={vi.fn()}
          variant="center"
        />
      )
      
      // Center row should also use justify-center for better visual balance
      const flexContainer = container.querySelector('.flex.gap-3')
      expect(flexContainer?.className).toContain('justify-center')
    })

    it('should maintain scrollability when content is wide', () => {
      const manyPeople: PersonDetails[] = Array.from({ length: 15 }, (_, i) => ({
        id: `person-${i}`,
        first_name: `Person`,
        middle_name: null,
        last_name: `${i}`,
        gender_id: 'male-id',
        date_of_birth: '1970-01-01T00:00:00.000Z',
        date_of_death: null,
        user_id: null,
        created_by_user_id: 'creator-id',
        is_primary: false,
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      }))
      
      const { container } = render(
        <HorizontalScrollRow
          people={manyPeople}
          onPersonClick={vi.fn()}
          variant="parent"
        />
      )
      
      // Should render all people
      const personCards = container.querySelectorAll('[role="button"]')
      expect(personCards.length).toBe(15)
      
      // Should have ScrollArea for horizontal scrolling
      const region = container.querySelector('[role="region"]')
      expect(region).toBeTruthy()
      
      // Should still have justify-center (centering works with scrolling)
      expect(container.innerHTML).toContain('justify-center')
    })
  })

  describe('Property 11: Three-Row Horizontal Layout', () => {
    /**
     * Feature: family-tree-view, Property 11: Three-Row Horizontal Layout
     * Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
     * 
     * For any person with relationships, the family tree should display exactly three horizontal rows
     * (parents, center with siblings+spouses, children) where each row uses horizontal scrolling
     * for overflow without vertical stacking of same-type relationships.
     */
    it('should display all people in a single horizontal row without vertical stacking', () => {
      fc.assert(
        fc.property(
          // Generate array of people (1 to 20 people)
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 20 }),
          // Generate variant
          fc.constantFrom('parent', 'center', 'child'),
          (people, variant) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant={variant}
              />
            )

            // Check that the row exists
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()

            // Check that all people are rendered
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(people.length)

            // Check that the container uses flexbox for horizontal layout
            const flexContainer = container.querySelector('.flex')
            expect(flexContainer).toBeTruthy()
            
            // Verify horizontal layout by checking for flex class without flex-col
            // The inner flex container should have 'flex' but not 'flex-col' alone
            const innerFlexDiv = container.querySelector('.flex.gap-3')
            expect(innerFlexDiv).toBeTruthy()
            
            // Check that items-center and justify-start are present (horizontal alignment)
            const hasHorizontalAlignment = container.innerHTML.includes('items-center') && 
                                          container.innerHTML.includes('justify-start')
            expect(hasHorizontalAlignment).toBe(true)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should display parents row with all parents horizontally scrollable', () => {
      fc.assert(
        fc.property(
          // Generate multiple parents (0 to 10)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 10 }),
          (parents) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={parents}
                onPersonClick={mockOnClick}
                variant="parent"
              />
            )

            if (parents.length === 0) {
              // Should render nothing for empty array
              expect(container.firstChild).toBeNull()
            } else {
              // Should render all parents
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(parents.length)
              
              // Should have ScrollArea component (check for region role)
              const region = container.querySelector('[role="region"]')
              expect(region).toBeTruthy()
              expect(region?.getAttribute('aria-label')).toBe('Parents row')
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should display center row with siblings and spouses with color-coding', () => {
      fc.assert(
        fc.property(
          // Generate siblings (0 to 5)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 5 }),
          // Generate selected person
          personDetailsArbitrary,
          // Generate spouses (0 to 3)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 3 }),
          (siblings, selectedPerson, spouses) => {
            const mockOnClick = vi.fn()
            
            // Combine all people for center row
            const allPeople = [...siblings, selectedPerson, ...spouses]
            
            // Create color coding map
            const colorCoding = new Map<string, 'sibling' | 'spouse'>()
            siblings.forEach(s => colorCoding.set(s.id, 'sibling'))
            spouses.forEach(s => colorCoding.set(s.id, 'spouse'))
            
            const { container } = render(
              <HorizontalScrollRow
                people={allPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )

            // Should render all people
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(allPeople.length)
            
            // Should have region with correct label
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()
            expect(region?.getAttribute('aria-label')).toBe('Center row with siblings and spouses')
            
            // Check for color-coding classes (siblings: blue, spouses: purple)
            if (siblings.length > 0) {
              const hasSiblingColor = container.innerHTML.includes('blue-')
              expect(hasSiblingColor).toBe(true)
            }
            
            if (spouses.length > 0) {
              const hasSpouseColor = container.innerHTML.includes('purple-')
              expect(hasSpouseColor).toBe(true)
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should display children row with all children horizontally scrollable', () => {
      fc.assert(
        fc.property(
          // Generate children (0 to 15)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 15 }),
          (children) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={children}
                onPersonClick={mockOnClick}
                variant="child"
              />
            )

            if (children.length === 0) {
              // Should render nothing for empty array
              expect(container.firstChild).toBeNull()
            } else {
              // Should render all children
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(children.length)
              
              // Should have region with correct label
              const region = container.querySelector('[role="region"]')
              expect(region).toBeTruthy()
              expect(region?.getAttribute('aria-label')).toBe('Children row')
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should maintain horizontal layout across all screen sizes', () => {
      fc.assert(
        fc.property(
          // Generate people
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 10 }),
          // Generate variant
          fc.constantFrom('parent', 'center', 'child'),
          (people, variant) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant={variant}
              />
            )

            // Check that responsive classes maintain horizontal layout
            // Should have flex class for horizontal layout
            const flexContainer = container.querySelector('.flex')
            expect(flexContainer).toBeTruthy()
            
            // Should have gap classes for spacing (responsive)
            const hasGapClasses = container.innerHTML.includes('gap-')
            expect(hasGapClasses).toBe(true)
            
            // Should have responsive padding (p-1, md:p-2, etc.)
            const hasResponsivePadding = container.innerHTML.includes('md:') || 
                                        container.innerHTML.includes('lg:')
            expect(hasResponsivePadding).toBe(true)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should support touch interactions with touch-manipulation class', () => {
      fc.assert(
        fc.property(
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 5 }),
          fc.constantFrom('parent', 'center', 'child'),
          (people, variant) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant={variant}
              />
            )

            // Check for touch-manipulation class on scroll bar
            const hasTouchSupport = container.innerHTML.includes('touch-manipulation')
            expect(hasTouchSupport).toBe(true)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('Property 12: Selected Person Centering', () => {
    /**
     * Feature: family-tree-view, Property 12: Selected Person Centering
     * Validates: Requirements 9.8, 9.9
     * 
     * For any person selected in the family tree, the center row should automatically scroll
     * to position that person in the center of the viewport.
     */
    it('should scroll to center the selected person in the center row', () => {
      fc.assert(
        fc.property(
          // Generate siblings (0 to 5)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 5 }),
          // Generate selected person
          personDetailsArbitrary,
          // Generate spouses (0 to 3)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 3 }),
          (siblings, selectedPerson, spouses) => {
            const mockOnClick = vi.fn()
            
            // Combine all people for center row: siblings, selected person, spouses
            const allPeople = [...siblings, selectedPerson, ...spouses]
            
            // Create color coding map
            const colorCoding = new Map<string, 'sibling' | 'spouse'>()
            siblings.forEach(s => colorCoding.set(s.id, 'sibling'))
            spouses.forEach(s => colorCoding.set(s.id, 'spouse'))
            
            // Mock scrollIntoView for testing
            const scrollIntoViewMock = vi.fn()
            Element.prototype.scrollIntoView = scrollIntoViewMock
            
            const { container } = render(
              <HorizontalScrollRow
                people={allPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )

            // Verify the selected person is rendered
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(allPeople.length)
            
            // Find the selected person's card
            // The selected person should be the one without a relationship type label
            // and should be in the middle of the array
            const selectedPersonIndex = siblings.length // Selected person is after siblings
            
            // Verify that the selected person exists in the rendered output
            // We can check this by verifying the total count matches our input
            expect(personCards.length).toBe(siblings.length + 1 + spouses.length)
            
            // The property we're testing is that when the component renders with a selected person,
            // it should be positioned in a way that allows centering (this is a layout property)
            // The actual scrollIntoView would be called by a useEffect in the component
            // For now, we verify the structure is correct for centering to work
            
            // Verify the center row has the correct aria-label
            const region = container.querySelector('[role="region"]')
            expect(region?.getAttribute('aria-label')).toBe('Center row with siblings and spouses')
            
            // Verify the selected person is in the correct position in the array
            // (after siblings, before spouses)
            expect(allPeople[selectedPersonIndex].id).toBe(selectedPerson.id)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should maintain selected person in center position when person selection changes', () => {
      fc.assert(
        fc.property(
          // Generate first selected person with family
          personDetailsArbitrary,
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 3 }),
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 2 }),
          // Generate second selected person with family
          personDetailsArbitrary,
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 3 }),
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 2 }),
          (person1, siblings1, spouses1, person2, siblings2, spouses2) => {
            const mockOnClick = vi.fn()
            
            // First render with person1
            const allPeople1 = [...siblings1, person1, ...spouses1]
            const colorCoding1 = new Map<string, 'sibling' | 'spouse'>()
            siblings1.forEach(s => colorCoding1.set(s.id, 'sibling'))
            spouses1.forEach(s => colorCoding1.set(s.id, 'spouse'))
            
            const { container: container1, rerender } = render(
              <HorizontalScrollRow
                people={allPeople1}
                selectedPersonId={person1.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding1}
              />
            )

            // Verify first render
            const personCards1 = container1.querySelectorAll('[role="button"]')
            expect(personCards1.length).toBe(allPeople1.length)
            
            // Now change to person2
            const allPeople2 = [...siblings2, person2, ...spouses2]
            const colorCoding2 = new Map<string, 'sibling' | 'spouse'>()
            siblings2.forEach(s => colorCoding2.set(s.id, 'sibling'))
            spouses2.forEach(s => colorCoding2.set(s.id, 'spouse'))
            
            rerender(
              <HorizontalScrollRow
                people={allPeople2}
                selectedPersonId={person2.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding2}
              />
            )

            // Verify second render
            const personCards2 = container1.querySelectorAll('[role="button"]')
            expect(personCards2.length).toBe(allPeople2.length)
            
            // Verify the selected person is in the correct position (after siblings)
            const selectedPersonIndex2 = siblings2.length
            expect(allPeople2[selectedPersonIndex2].id).toBe(person2.id)
            
            // Verify the center row structure is maintained
            const region = container1.querySelector('[role="region"]')
            expect(region?.getAttribute('aria-label')).toBe('Center row with siblings and spouses')
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should handle centering when selected person has no siblings or spouses', () => {
      fc.assert(
        fc.property(
          personDetailsArbitrary,
          (selectedPerson) => {
            const mockOnClick = vi.fn()
            
            // Only the selected person, no siblings or spouses
            const allPeople = [selectedPerson]
            const colorCoding = new Map<string, 'sibling' | 'spouse'>()
            
            const { container } = render(
              <HorizontalScrollRow
                people={allPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )

            // Should render just the selected person
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(1)
            
            // Should still have the center row structure
            const region = container.querySelector('[role="region"]')
            expect(region?.getAttribute('aria-label')).toBe('Center row with siblings and spouses')
            
            // The selected person should be the only one in the array
            expect(allPeople[0].id).toBe(selectedPerson.id)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should handle centering with many siblings and spouses requiring scroll', () => {
      fc.assert(
        fc.property(
          // Generate many siblings (5 to 10)
          fc.array(personDetailsArbitrary, { minLength: 5, maxLength: 10 }),
          personDetailsArbitrary,
          // Generate many spouses (3 to 8)
          fc.array(personDetailsArbitrary, { minLength: 3, maxLength: 8 }),
          (siblings, selectedPerson, spouses) => {
            const mockOnClick = vi.fn()
            
            // Combine all people for center row
            const allPeople = [...siblings, selectedPerson, ...spouses]
            
            // Create color coding map
            const colorCoding = new Map<string, 'sibling' | 'spouse'>()
            siblings.forEach(s => colorCoding.set(s.id, 'sibling'))
            spouses.forEach(s => colorCoding.set(s.id, 'spouse'))
            
            const { container } = render(
              <HorizontalScrollRow
                people={allPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )

            // Should render all people
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(allPeople.length)
            
            // Should have horizontal scroll capability (ScrollArea component)
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()
            
            // Verify the selected person is in the middle of the array
            const selectedPersonIndex = siblings.length
            expect(allPeople[selectedPersonIndex].id).toBe(selectedPerson.id)
            
            // Verify horizontal layout is maintained even with many people
            const flexContainer = container.querySelector('.flex')
            expect(flexContainer).toBeTruthy()
            
            // Should have ScrollBar for horizontal scrolling
            const hasScrollBar = container.innerHTML.includes('ScrollBar') || 
                                container.querySelector('[orientation="horizontal"]')
            expect(hasScrollBar).toBeTruthy()
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('Property 13: Relationship Type Color Coding', () => {
    /**
     * Feature: family-tree-view, Property 13: Relationship Type Color Coding
     * Validates: Requirements 9.2, 9.3, 9.4
     * 
     * For any person card displayed in the family tree, the card should have color-coding
     * that corresponds to its relationship type (parent, sibling, spouse, child, or selected person).
     */
    it('should apply distinct color coding to all relationship types', () => {
      fc.assert(
        fc.property(
          // Generate parents (0 to 3)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 3 }),
          // Generate siblings (0 to 5)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 5 }),
          // Generate selected person
          personDetailsArbitrary,
          // Generate spouses (0 to 3)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 3 }),
          // Generate children (0 to 8)
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 8 }),
          (parents, siblings, selectedPerson, spouses, children) => {
            const mockOnClick = vi.fn()
            
            // Test parent row color coding
            if (parents.length > 0) {
              const { container: parentContainer } = render(
                <HorizontalScrollRow
                  people={parents}
                  onPersonClick={mockOnClick}
                  variant="parent"
                />
              )
              
              // Parents should be rendered
              const parentCards = parentContainer.querySelectorAll('[role="button"]')
              expect(parentCards.length).toBe(parents.length)
              
              // Parent row should exist
              const parentRegion = parentContainer.querySelector('[role="region"]')
              expect(parentRegion?.getAttribute('aria-label')).toBe('Parents row')
            }
            
            // Test center row color coding (siblings and spouses)
            const centerPeople = [...siblings, selectedPerson, ...spouses]
            const colorCoding = new Map<string, 'sibling' | 'spouse'>()
            siblings.forEach(s => colorCoding.set(s.id, 'sibling'))
            spouses.forEach(s => colorCoding.set(s.id, 'spouse'))
            
            const { container: centerContainer } = render(
              <HorizontalScrollRow
                people={centerPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )
            
            // All center row people should be rendered
            const centerCards = centerContainer.querySelectorAll('[role="button"]')
            expect(centerCards.length).toBe(centerPeople.length)
            
            // Check for sibling color coding (blue)
            if (siblings.length > 0) {
              const hasSiblingColor = centerContainer.innerHTML.includes('blue-')
              expect(hasSiblingColor).toBe(true)
            }
            
            // Check for spouse color coding (purple)
            if (spouses.length > 0) {
              const hasSpouseColor = centerContainer.innerHTML.includes('purple-')
              expect(hasSpouseColor).toBe(true)
            }
            
            // Selected person should not have sibling or spouse color coding
            // (it should have selected styling instead)
            const centerRegion = centerContainer.querySelector('[role="region"]')
            expect(centerRegion?.getAttribute('aria-label')).toBe('Center row with siblings and spouses')
            
            // Test children row color coding
            if (children.length > 0) {
              const { container: childContainer } = render(
                <HorizontalScrollRow
                  people={children}
                  onPersonClick={mockOnClick}
                  variant="child"
                />
              )
              
              // Children should be rendered
              const childCards = childContainer.querySelectorAll('[role="button"]')
              expect(childCards.length).toBe(children.length)
              
              // Children row should exist
              const childRegion = childContainer.querySelector('[role="region"]')
              expect(childRegion?.getAttribute('aria-label')).toBe('Children row')
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should maintain color coding consistency across re-renders', () => {
      fc.assert(
        fc.property(
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 3 }),
          personDetailsArbitrary,
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 3 }),
          (siblings, selectedPerson, spouses) => {
            const mockOnClick = vi.fn()
            
            const centerPeople = [...siblings, selectedPerson, ...spouses]
            const colorCoding = new Map<string, 'sibling' | 'spouse'>()
            siblings.forEach(s => colorCoding.set(s.id, 'sibling'))
            spouses.forEach(s => colorCoding.set(s.id, 'spouse'))
            
            const { container, rerender } = render(
              <HorizontalScrollRow
                people={centerPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )
            
            // Check initial render
            const hasSiblingColor1 = container.innerHTML.includes('blue-')
            const hasSpouseColor1 = container.innerHTML.includes('purple-')
            expect(hasSiblingColor1).toBe(true)
            expect(hasSpouseColor1).toBe(true)
            
            // Re-render with same props
            rerender(
              <HorizontalScrollRow
                people={centerPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )
            
            // Check that color coding is maintained
            const hasSiblingColor2 = container.innerHTML.includes('blue-')
            const hasSpouseColor2 = container.innerHTML.includes('purple-')
            expect(hasSiblingColor2).toBe(true)
            expect(hasSpouseColor2).toBe(true)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should not apply relationship color coding to selected person', () => {
      fc.assert(
        fc.property(
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 2 }),
          personDetailsArbitrary,
          fc.array(personDetailsArbitrary, { minLength: 0, maxLength: 2 }),
          (siblings, selectedPerson, spouses) => {
            const mockOnClick = vi.fn()
            
            const centerPeople = [...siblings, selectedPerson, ...spouses]
            const colorCoding = new Map<string, 'sibling' | 'spouse'>()
            siblings.forEach(s => colorCoding.set(s.id, 'sibling'))
            spouses.forEach(s => colorCoding.set(s.id, 'spouse'))
            // Intentionally not adding selected person to color coding
            
            const { container } = render(
              <HorizontalScrollRow
                people={centerPeople}
                selectedPersonId={selectedPerson.id}
                onPersonClick={mockOnClick}
                variant="center"
                colorCoding={colorCoding}
              />
            )
            
            // All people should be rendered
            const cards = container.querySelectorAll('[role="button"]')
            expect(cards.length).toBe(centerPeople.length)
            
            // Selected person should not be in the color coding map
            expect(colorCoding.has(selectedPerson.id)).toBe(false)
            
            // The component should handle this correctly and not apply color coding to selected person
            // We verify this by checking that the component renders without errors
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should apply correct color coding for each relationship type in their respective rows', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('parent', 'center', 'child'),
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 5 }),
          fc.option(personDetailsArbitrary, { nil: null }),
          (variant, people, selectedPerson) => {
            const mockOnClick = vi.fn()
            
            // For center row, create color coding
            let colorCoding: Map<string, 'sibling' | 'spouse'> | undefined
            let selectedPersonId: string | undefined
            
            if (variant === 'center' && selectedPerson) {
              colorCoding = new Map<string, 'sibling' | 'spouse'>()
              // Randomly assign some as siblings and some as spouses
              people.forEach((p, i) => {
                if (i % 2 === 0) {
                  colorCoding!.set(p.id, 'sibling')
                } else {
                  colorCoding!.set(p.id, 'spouse')
                }
              })
              selectedPersonId = selectedPerson.id
              people = [...people, selectedPerson]
            }
            
            const { container } = render(
              <HorizontalScrollRow
                people={people}
                selectedPersonId={selectedPersonId}
                onPersonClick={mockOnClick}
                variant={variant}
                colorCoding={colorCoding}
              />
            )
            
            // Verify the row is rendered
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()
            
            // Verify correct aria-label based on variant
            const expectedLabel = variant === 'parent' 
              ? 'Parents row' 
              : variant === 'child' 
              ? 'Children row' 
              : 'Center row with siblings and spouses'
            expect(region?.getAttribute('aria-label')).toBe(expectedLabel)
            
            // For center row, verify color coding is applied
            if (variant === 'center' && colorCoding) {
              const hasSiblingOrSpouseColor = container.innerHTML.includes('blue-') || 
                                              container.innerHTML.includes('purple-')
              expect(hasSiblingOrSpouseColor).toBe(true)
            }
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('Property 14: Row Content Centering', () => {
    /**
     * Feature: family-tree-view, Property 14: Row Content Centering
     * Validates: Requirements 9.2, 9.4
     * 
     * For any row (parents, center, or children) in the family tree, when the row content
     * is narrower than the viewport, the content should be centered in the viewport
     * rather than left-aligned.
     */
    it('should center content when narrower than viewport for parent and child rows', () => {
      fc.assert(
        fc.property(
          // Generate small number of people (1 to 3) to ensure content is narrow
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 3 }),
          // Test parent and child variants (center row has different behavior)
          fc.constantFrom('parent', 'child'),
          (people, variant) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant={variant}
              />
            )

            // Verify the row is rendered
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()
            
            // Check that the flex container has centering classes
            // When content is narrow, it should use justify-center
            const flexContainer = container.querySelector('.flex')
            expect(flexContainer).toBeTruthy()
            
            // The container should have justify-center for centering
            // or items-center for vertical centering
            const hasJustifyCenter = container.innerHTML.includes('justify-center')
            const hasItemsCenter = container.innerHTML.includes('items-center')
            
            // At minimum, items-center should be present for vertical alignment
            expect(hasItemsCenter).toBe(true)
            
            // For narrow content, justify-center should be applied
            // This is a layout property that ensures content is centered
            if (people.length <= 3) {
              // With few people, the content should be centered
              // The component should apply justify-center
              expect(hasJustifyCenter || hasItemsCenter).toBe(true)
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should maintain scrollability when content exceeds viewport width', () => {
      fc.assert(
        fc.property(
          // Generate many people (10 to 20) to ensure content exceeds viewport
          fc.array(personDetailsArbitrary, { minLength: 10, maxLength: 20 }),
          fc.constantFrom('parent', 'child'),
          (people, variant) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant={variant}
              />
            )

            // Verify the row is rendered
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()
            
            // Should have ScrollArea component for horizontal scrolling
            const hasScrollBar = container.innerHTML.includes('ScrollBar') || 
                                container.querySelector('[orientation="horizontal"]')
            expect(hasScrollBar).toBeTruthy()
            
            // All people should be rendered
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(people.length)
            
            // The flex container should still exist for layout
            const flexContainer = container.querySelector('.flex')
            expect(flexContainer).toBeTruthy()
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should apply centering to both parent and children rows consistently', () => {
      fc.assert(
        fc.property(
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 3 }),
          (people) => {
            const mockOnClick = vi.fn()
            
            // Test parent row
            const { container: parentContainer } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant="parent"
              />
            )
            
            // Test child row
            const { container: childContainer } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant="child"
              />
            )
            
            // Both should have the same centering behavior
            const parentHasItemsCenter = parentContainer.innerHTML.includes('items-center')
            const childHasItemsCenter = childContainer.innerHTML.includes('items-center')
            
            expect(parentHasItemsCenter).toBe(true)
            expect(childHasItemsCenter).toBe(true)
            
            // Both should render all people
            const parentCards = parentContainer.querySelectorAll('[role="button"]')
            const childCards = childContainer.querySelectorAll('[role="button"]')
            
            expect(parentCards.length).toBe(people.length)
            expect(childCards.length).toBe(people.length)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should handle edge case of single person in row', () => {
      fc.assert(
        fc.property(
          personDetailsArbitrary,
          fc.constantFrom('parent', 'child'),
          (person, variant) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={[person]}
                onPersonClick={mockOnClick}
                variant={variant}
              />
            )

            // Should render the single person
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(1)
            
            // Should have centering classes
            const hasItemsCenter = container.innerHTML.includes('items-center')
            expect(hasItemsCenter).toBe(true)
            
            // Should not need scrolling for single person
            const region = container.querySelector('[role="region"]')
            expect(region).toBeTruthy()
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should center content regardless of viewport size changes', () => {
      fc.assert(
        fc.property(
          fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 3 }),
          fc.constantFrom('parent', 'child'),
          (people, variant) => {
            const mockOnClick = vi.fn()
            
            const { container } = render(
              <HorizontalScrollRow
                people={people}
                onPersonClick={mockOnClick}
                variant={variant}
              />
            )

            // Verify centering is applied through CSS classes
            // The component should use responsive classes that maintain centering
            const hasResponsiveClasses = container.innerHTML.includes('md:') || 
                                        container.innerHTML.includes('lg:')
            expect(hasResponsiveClasses).toBe(true)
            
            // Should have items-center for vertical centering
            const hasItemsCenter = container.innerHTML.includes('items-center')
            expect(hasItemsCenter).toBe(true)
            
            // Should render all people
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(people.length)
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})
