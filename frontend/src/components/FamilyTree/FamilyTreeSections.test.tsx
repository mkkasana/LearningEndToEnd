import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import * as fc from 'fast-check'
import { ParentsSection } from './ParentsSection'
import { SiblingsSection } from './SiblingsSection'
import { ChildrenSection } from './ChildrenSection'
import { SpouseSection } from './SpouseSection'

// Generator for PersonDetails
const personDetailsArbitrary = fc.record({
  id: fc.uuid(),
  first_name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  middle_name: fc.option(fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0), { nil: null }),
  last_name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  gender_id: fc.constantFrom('gen-6a0ede824d101', 'gen-6a0ede824d102'), // Male or Female
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
  created_at: fc.integer({ min: 1609459200000, max: Date.now() }).map(ts => new Date(ts).toISOString()),
  updated_at: fc.integer({ min: 1609459200000, max: Date.now() }).map(ts => new Date(ts).toISOString()),
})

describe('FamilyTree Sections - Property-Based Tests', () => {
  /**
   * Feature: family-tree-view, Property 4: Relationship Display
   * Validates: Requirements 3.1, 4.1, 5.1, 6.1
   * 
   * For any person with relationships of a given type (parents, spouses, siblings, or children),
   * when that person is selected, the family tree should display all relationships of that type
   * in the appropriate section.
   */
  describe('Property 4: Relationship Display', () => {
    describe('ParentsSection', () => {
      it('should display all parent relationships when parents exist', () => {
        fc.assert(
          fc.property(
            fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 2 }),
            (parents) => {
              // Ensure unique IDs to avoid deduplication
              const uniqueParents = parents.map((p, idx) => ({
                ...p,
                id: `parent-${idx}-${p.id}`
              }))
              
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <ParentsSection parents={uniqueParents} onPersonClick={mockOnClick} />
              )

              // Verify the correct number of person cards are rendered
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(uniqueParents.length)
              
              // Verify each parent's name appears somewhere in the rendered output
              for (const parent of uniqueParents) {
                const displayName = `${parent.first_name} ${parent.last_name}`.trim()
                const nameElements = Array.from(container.querySelectorAll('.font-semibold'))
                const hasName = nameElements.some(el => el.textContent?.trim() === displayName)
                expect(hasName).toBe(true)
              }
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should render nothing when no parents exist', () => {
        const mockOnClick = vi.fn()
        
        const { container } = render(
          <ParentsSection parents={[]} onPersonClick={mockOnClick} />
        )

        // Verify that no person cards are rendered
        const personCards = container.querySelectorAll('[role="button"]')
        expect(personCards.length).toBe(0)
      })

      it('should handle single parent case', () => {
        fc.assert(
          fc.property(
            personDetailsArbitrary,
            (parent) => {
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <ParentsSection parents={[parent]} onPersonClick={mockOnClick} />
              )

              // Verify that exactly one parent card is displayed
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(1)

              // Verify the parent's name is displayed
              const displayName = `${parent.first_name} ${parent.last_name}`.trim()
              const nameElements = Array.from(container.querySelectorAll('.font-semibold'))
              const hasName = nameElements.some(el => el.textContent?.trim() === displayName)
              expect(hasName).toBe(true)
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should handle two parents case (mother and father)', () => {
        fc.assert(
          fc.property(
            personDetailsArbitrary,
            personDetailsArbitrary,
            (parent1, parent2) => {
              // Ensure different genders
              const father = { ...parent1, gender_id: 'gen-6a0ede824d101' }
              const mother = { ...parent2, gender_id: 'gen-6a0ede824d102' }
              
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <ParentsSection parents={[father, mother]} onPersonClick={mockOnClick} />
              )

              // Verify that exactly two parent cards are displayed
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(2)

              // Verify both parents' names are displayed
              const fatherName = `${father.first_name} ${father.last_name}`.trim()
              const motherName = `${mother.first_name} ${mother.last_name}`.trim()
              
              const nameElements = Array.from(container.querySelectorAll('.font-semibold'))
              const hasFather = nameElements.some(el => el.textContent?.trim() === fatherName)
              const hasMother = nameElements.some(el => el.textContent?.trim() === motherName)
              
              expect(hasFather).toBe(true)
              expect(hasMother).toBe(true)
            }
          ),
          { numRuns: 100 }
        )
      })
    })

    // Note: Tests for SiblingsSection and ChildrenSection
    // will be added as those components are implemented

    describe('SpouseSection', () => {
      /**
       * Feature: family-tree-view, Property 5: Multiple Spouse Display
       * Validates: Requirements 4.4
       * 
       * For any person with multiple spouse relationships, all spouses should be accessible
       * through a carousel with navigation controls, with no spouses omitted.
       */
      it('should display all spouses when multiple spouses exist', () => {
        fc.assert(
          fc.property(
            fc.array(personDetailsArbitrary, { minLength: 2, maxLength: 5 }),
            (spouses) => {
              // Ensure unique IDs to avoid deduplication
              const uniqueSpouses = spouses.map((s, idx) => ({
                ...s,
                id: `spouse-${idx}-${s.id}`
              }))
              
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <SpouseSection spouses={uniqueSpouses} onPersonClick={mockOnClick} />
              )

              // For multiple spouses, a carousel is used which shows only one spouse at a time
              // Verify that exactly one person card is displayed (the current spouse)
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(1)

              // Verify navigation controls are present
              const prevButton = container.querySelector('[aria-label="Previous spouse"]')
              const nextButton = container.querySelector('[aria-label="Next spouse"]')
              expect(prevButton).toBeTruthy()
              expect(nextButton).toBeTruthy()

              // Verify indicator dots are present (one for each spouse)
              const dots = container.querySelectorAll('[role="tab"]')
              expect(dots.length).toBe(uniqueSpouses.length)

              // Verify the first spouse is displayed initially
              const firstSpouse = uniqueSpouses[0]
              const displayName = `${firstSpouse.first_name} ${firstSpouse.last_name}`.trim()
              const nameElements = Array.from(container.querySelectorAll('.font-semibold'))
              const hasName = nameElements.some(el => el.textContent?.trim() === displayName)
              expect(hasName).toBe(true)
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should display single spouse correctly', () => {
        fc.assert(
          fc.property(
            personDetailsArbitrary,
            (spouse) => {
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <SpouseSection spouses={[spouse]} onPersonClick={mockOnClick} />
              )

              // Verify exactly one spouse card is displayed
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(1)
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should render nothing when no spouses exist', () => {
        const mockOnClick = vi.fn()
        
        const { container } = render(
          <SpouseSection spouses={[]} onPersonClick={mockOnClick} />
        )

        // Verify no person cards are rendered
        const personCards = container.querySelectorAll('[role="button"]')
        expect(personCards.length).toBe(0)
      })
    })

    describe('SiblingsSection', () => {
      /**
       * Feature: family-tree-view, Property 6: Multiple Sibling Display
       * Validates: Requirements 5.3
       * 
       * For any person with more than a threshold number of siblings, all siblings should be
       * displayed in a horizontally scrollable container, with no siblings omitted.
       */
      it('should display all siblings when multiple siblings exist', () => {
        fc.assert(
          fc.property(
            fc.array(personDetailsArbitrary, { minLength: 2, maxLength: 10 }),
            (siblings) => {
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <SiblingsSection siblings={siblings} onPersonClick={mockOnClick} />
              )

              // Verify that all siblings are displayed
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(siblings.length)

              // Verify each sibling card has the sibling variant styling
              personCards.forEach((card) => {
                // Sibling variant has opacity-75 and scale-90 classes
                expect(card.className).toContain('opacity-75')
                expect(card.className).toContain('scale-90')
              })
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should display single sibling correctly', () => {
        fc.assert(
          fc.property(
            personDetailsArbitrary,
            (sibling) => {
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <SiblingsSection siblings={[sibling]} onPersonClick={mockOnClick} />
              )

              // Verify exactly one sibling card is displayed
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(1)
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should render nothing when no siblings exist', () => {
        const mockOnClick = vi.fn()
        
        const { container } = render(
          <SiblingsSection siblings={[]} onPersonClick={mockOnClick} />
        )

        // Verify no person cards are rendered
        const personCards = container.querySelectorAll('[role="button"]')
        expect(personCards.length).toBe(0)
      })
    })

    describe('ChildrenSection', () => {
      /**
       * Feature: family-tree-view, Property 7: All Children Display
       * Validates: Requirements 6.5
       * 
       * For any person with children from multiple spouses, all children should be displayed
       * regardless of which spouse they are associated with, with no children omitted.
       */
      it('should display all children regardless of spouse association', () => {
        fc.assert(
          fc.property(
            fc.array(personDetailsArbitrary, { minLength: 1, maxLength: 10 }),
            (children) => {
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <ChildrenSection children={children} onPersonClick={mockOnClick} />
              )

              // Verify that all children are displayed
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(children.length)

              // Verify each child card has the child variant styling
              personCards.forEach((card) => {
                // Child variant has scale-95 class
                expect(card.className).toContain('scale-95')
              })
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should display single child correctly', () => {
        fc.assert(
          fc.property(
            personDetailsArbitrary,
            (child) => {
              const mockOnClick = vi.fn()
              
              const { container } = render(
                <ChildrenSection children={[child]} onPersonClick={mockOnClick} />
              )

              // Verify exactly one child card is displayed
              const personCards = container.querySelectorAll('[role="button"]')
              expect(personCards.length).toBe(1)
            }
          ),
          { numRuns: 100 }
        )
      })

      it('should render nothing when no children exist', () => {
        const mockOnClick = vi.fn()
        
        const { container } = render(
          <ChildrenSection children={[]} onPersonClick={mockOnClick} />
        )

        // Verify no person cards are rendered
        const personCards = container.querySelectorAll('[role="button"]')
        expect(personCards.length).toBe(0)
      })
    })
  })
})
