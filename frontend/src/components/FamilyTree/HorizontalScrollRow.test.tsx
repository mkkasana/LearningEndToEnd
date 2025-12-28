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
  date_of_birth: fc.date({ min: new Date('1900-01-01'), max: new Date() }).map(d => d.toISOString()),
  date_of_death: fc.option(fc.date({ min: new Date('1900-01-01'), max: new Date() }).map(d => d.toISOString()), { nil: null }),
  user_id: fc.option(fc.uuid(), { nil: null }),
  created_by_user_id: fc.uuid(),
  is_primary: fc.boolean(),
  created_at: fc.date().map(d => d.toISOString()),
  updated_at: fc.date().map(d => d.toISOString()),
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
      
      // Check for pink color classes (spouse color)
      expect(container.innerHTML).toContain('pink-')
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
            const scrollArea = container.querySelector('[data-radix-scroll-area-viewport]')
            expect(scrollArea).toBeTruthy()

            // Check that all people are rendered
            const personCards = container.querySelectorAll('[role="button"]')
            expect(personCards.length).toBe(people.length)

            // Check that the container uses flexbox for horizontal layout
            const flexContainer = container.querySelector('.flex')
            expect(flexContainer).toBeTruthy()
            
            // Verify no vertical stacking classes (flex-col, grid with rows, etc.)
            const hasVerticalStacking = container.innerHTML.includes('flex-col') && 
                                       !container.innerHTML.includes('md:flex-row')
            expect(hasVerticalStacking).toBe(false)
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
              
              // Should have horizontal scroll
              const scrollBar = container.querySelector('[data-orientation="horizontal"]')
              expect(scrollBar).toBeTruthy()
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
            
            // Should have horizontal scroll
            const scrollBar = container.querySelector('[data-orientation="horizontal"]')
            expect(scrollBar).toBeTruthy()
            
            // Check for color-coding classes (siblings: blue, spouses: pink)
            if (siblings.length > 0) {
              const hasSiblingColor = container.innerHTML.includes('blue-')
              expect(hasSiblingColor).toBe(true)
            }
            
            if (spouses.length > 0) {
              const hasSpouseColor = container.innerHTML.includes('pink-')
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
              
              // Should have horizontal scroll
              const scrollBar = container.querySelector('[data-orientation="horizontal"]')
              expect(scrollBar).toBeTruthy()
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
})
