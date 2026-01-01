# Requirements Document

## Introduction

This feature enhances the Family Tree View by adding an "Add Family Member" placeholder card (with a "+" icon) at the rightmost position of each relationship row (Parents, Center/Siblings+Spouses, Children). When clicked, this card initiates the same "Add Family Member" flow that exists in the "Update Family" page, allowing users to add family members directly from the Family Tree without navigating away.

## Glossary

- **Family_Tree_View**: The visual representation of family relationships displayed in three horizontal rows
- **Add_Card**: A placeholder card with a "+" icon that triggers the Add Family Member flow
- **Parents_Row**: The top row displaying parent relationships (Father, Mother)
- **Center_Row**: The middle row displaying siblings, the selected person, and spouses
- **Children_Row**: The bottom row displaying children (Son, Daughter)
- **Discovery_Dialog**: The initial dialog that searches for potential family connections before manual entry
- **Add_Family_Member_Wizard**: The multi-step wizard for manually entering family member details

## Requirements

### Requirement 1: Add Card Display in Each Row

**User Story:** As a user viewing the Family Tree, I want to see an "Add" card at the end of each relationship row, so that I can quickly add new family members without leaving the tree view.

#### Acceptance Criteria

1. WHEN the Family Tree View renders the Parents row, THE System SHALL display an Add_Card at the rightmost position after all existing parent cards
2. WHEN the Family Tree View renders the Center row, THE System SHALL display an Add_Card at the rightmost position after all existing sibling and spouse cards
3. WHEN the Family Tree View renders the Children row, THE System SHALL display an Add_Card at the rightmost position after all existing child cards
4. WHEN a row has no existing family members, THE System SHALL still display the Add_Card in that row
5. THE Add_Card SHALL display a "+" icon centered within the card
6. THE Add_Card SHALL have visual styling that distinguishes it from person cards (e.g., dashed border, muted background) but the size wise dimensions should be same as other cards, This card should have a circle in mid of it and that circle would bave + sign.


### Requirement 2: Pre-filtered Relationship Types

**User Story:** As a user adding a family member from a specific row, I dont want the relationship type to be contextually pre-filtered, Lets list all and let user decided whatever they want to create.


### Requirement 3: Family Tree Refresh After Addition

**User Story:** As a user who just added a family member, I want the Family Tree to automatically update, so that I can see the new member in the tree immediately.

#### Acceptance Criteria

1. WHEN a user successfully adds a family member via the Add_Card flow, THE System SHALL refresh the Family Tree data
2. WHEN the Family Tree data refreshes, THE System SHALL display the newly added family member in the appropriate row
3. WHEN the addition is cancelled or fails, THE System SHALL maintain the current Family Tree state without changes

### Requirement 4: Accessibility

**User Story:** As a user with accessibility needs, I want the Add card to be fully accessible, so that I can use it with assistive technologies.

#### Acceptance Criteria
1. Not just empty person card with + sign in it should be sufficient, dont add too much text and dont make it complex.

### Requirement 5: Empty State Enhancement

**User Story:** As a user with no family relationships, I want to see Add cards for each relationship type, so that I can start building my family tree.

#### Acceptance Criteria

1. WHEN the Family Tree has no relationships, THE System SHALL display Add_Cards for Parents, Siblings/Spouses, and Children rows
2. THE empty state Add_Cards SHALL maintain the same visual hierarchy as the populated tree (Parents on top, Center in middle, Children at bottom)
