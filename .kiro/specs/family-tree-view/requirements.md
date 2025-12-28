# Requirements Document

## Introduction

This document specifies the requirements for a Family Tree View feature that provides users with an interactive, visual representation of family relationships. The feature centers on a selected person and displays their immediate family (parents, spouse, siblings, and children) in a focused tree layout, allowing users to navigate through the family tree by selecting different family members.

## Glossary

- **System**: The full-stack FastAPI application with React frontend
- **User**: An authenticated person using the application
- **Selected Person**: The person currently at the center of the family tree view
- **Family Tree View**: A visual representation of family relationships centered on a selected person
- **Person Card**: A UI component displaying information about a family member
- **Relationship Line**: A visual connector showing the relationship between two people
- **Progressive Loading**: Loading additional family data on-demand as the user navigates

## Requirements

### Requirement 1

**User Story:** As a user, I want to access a Family Tree View from the main navigation, so that I can visualize my family relationships.

#### Acceptance Criteria

1. WHEN the application loads THEN the System SHALL display a "Family View" tab in the main navigation alongside Dashboard, Update Family, and other tabs
2. WHEN a user clicks the "Family View" tab THEN the System SHALL navigate to the Family Tree View page
3. WHEN the Family Tree View page loads THEN the System SHALL display the family tree centered on the current authenticated user's person profile
4. WHEN the user's person profile does not exist THEN the System SHALL display an appropriate message prompting profile completion

### Requirement 2

**User Story:** As a user, I want to see the selected person prominently displayed in the center of the family tree, so that I can easily identify whose family I am viewing.

#### Acceptance Criteria

1. WHEN the Family Tree View renders THEN the System SHALL display the selected person's card at the center of the view
2. WHEN displaying the selected person's card THEN the System SHALL show the person's First name & Last name and below name show "birth year - death" year if applicable else just "birth year -"
3. WHEN displaying the selected person's card THEN the System SHALL visually distinguish it from other person cards through size, border, or background styling
4. WHEN the selected person has a profile photo THEN the System SHALL display the photo in the person card.
5. WHEN the selected person does not have a profile photo THEN the System SHALL display a default male/female avatar or placeholder

### Requirement 3

**User Story:** As a user, I want to see the selected person's parents displayed above them in the family tree, so that I can understand their ancestry.

#### Acceptance Criteria

1. WHEN the selected person has parent relationships THEN the System SHALL display parent cards above the selected person's card
2. WHEN displaying parent cards THEN the System SHALL show mother and father side-by-side
3. WHEN displaying parent cards THEN the System SHALL connect them to the selected person with downward-pointing visual lines
4. WHEN displaying each parent card THEN the System SHALL show the parent's First name & Last name and below name show "birth year - death" year if applicable else just "birth year -"
5. WHEN only one parent is known THEN the System SHALL display only the available parent
6. WHEN no parent data exists THEN the System SHALL display an empty state or placeholder indicating no parents are recorded

### Requirement 4

**User Story:** As a user, I want to see the selected person's spouse displayed next to them, so that I can understand their marital relationships.

#### Acceptance Criteria

1. WHEN the selected person has a spouse relationship THEN the System SHALL display the spouse card horizontally adjacent to the selected person's card
2. WHEN displaying the spouse card THEN the System SHALL connect it to the selected person with a horizontal relationship line
3. WHEN displaying the spouse card THEN the System SHALL show the spouse's name, birth year, and death year if applicable
4. WHEN the selected person has multiple spouses THEN the System SHALL display all the  spouse next to each other in horizontelly scrolable list or slideshow kind of thing.
5. WHEN the selected person has no spouse THEN the System SHALL not display a spouse card

### Requirement 5

**User Story:** As a user, I want to see the selected person's siblings displayed near them, so that I have contextual awareness of their family structure without overwhelming the view.

#### Acceptance Criteria

1. WHEN the selected person has siblings THEN the System SHALL display sibling cards near the selected person
2. WHEN displaying sibling cards THEN the System SHALL visually de-emphasize them through reduced size or opacity compared to the selected person
3. WHEN the selected person has more than a threshold number of siblings THEN the System SHALL display both side of person in horizontelly scrolable list,
5. WHEN the selected person has no siblings THEN the System SHALL not display sibling cards

### Requirement 6

**User Story:** As a user, I want to see the selected person's children displayed below them in the family tree, so that I can understand their descendants.

#### Acceptance Criteria

1. WHEN the selected person has child relationships THEN the System SHALL display child cards below the selected person's card
2. WHEN displaying child cards THEN the System SHALL connect them to the selected person with downward-branching visual lines
3. WHEN displaying each child card THEN the System SHALL show the child's name and birth, death year same as above.
4. WHEN displaying child cards THEN the System SHALL make them visually smaller than the selected person's card
5. WHEN the selected person has children from multiple spouses THEN the System SHALL show all children irrespective of spouse.
6. WHEN the selected person has no children THEN the System SHALL not display child cards

### Requirement 7

**User Story:** As a user, I want to click on any person in the family tree to make them the new selected person, so that I can navigate through the family tree.

#### Acceptance Criteria

1. WHEN a user clicks on any person card in the family tree THEN the System SHALL make that person the new selected person
2. WHEN a new person is selected THEN the System SHALL re-center the family tree view on that person
3. WHEN a new person is selected THEN the System SHALL fetch that person's family relationship data
4. WHEN a new person is selected THEN the System SHALL redraw the family tree with smooth animation transitions
5. WHEN fetching new family data THEN the System SHALL display a loading indicator

### Requirement 8 [Optional as P2]

**User Story:** As a user, I want to expand additional generations of the family tree on demand, so that I can explore extended family without loading everything at once.

#### Acceptance Criteria

1. WHEN a person has additional ancestors not currently visible THEN the System SHALL display an expand control on their parent section
2. WHEN a person has additional descendants not currently visible THEN the System SHALL display an expand control on their children section
3. WHEN a user clicks an expand control THEN the System SHALL load and display the additional generation of family members
4. WHEN loading additional generations THEN the System SHALL display a loading indicator
5. WHEN additional generations are loaded THEN the System SHALL animate the expansion smoothly


### Requirement 9

**User Story:** As a user, I want the family tree view to be responsive and work well on different screen sizes, so that I can view my family tree on any device.

#### Acceptance Criteria

1. WHEN the Family Tree View renders THEN the System SHALL display exactly three horizontal rows: parents (top), siblings and spouses (middle), and children (bottom)
2. WHEN a person has multiple parents THEN the System SHALL display all parents in a single horizontally scrollable row at the top with color-coding to identify parents, centered in the viewport
3. WHEN a person has multiple siblings and/or spouses THEN the System SHALL display all siblings and spouses together in a single horizontally scrollable middle row with color-coding to differentiate relationship types
4. WHEN a person has multiple children THEN the System SHALL display all children in a single horizontally scrollable row at the bottom with color-coding to identify children, centered in the viewport
5. WHEN the Family Tree View renders on any screen size THEN the System SHALL maintain the three-row horizontal layout without vertical stacking of same-type relationships
6. WHEN the viewport size changes THEN the System SHALL adjust card sizes and spacing while maintaining horizontal scrollability
7. WHEN touch gestures are available THEN the System SHALL support touch interactions for selecting persons and horizontal scrolling
8. WHEN the Family Tree View initially renders THEN the System SHALL scroll the center row to position the selected person in the center of the viewport
9. WHEN a new person is selected THEN the System SHALL scroll the center row to center the newly selected person in the viewport
10. WHEN displaying person cards THEN the System SHALL use distinct, light colors for each relationship type (parents, siblings, spouses, children, selected) that are easily distinguishable from each other

### Requirement 10

**User Story:** As a user, I want to search for any person in the system regardless of family connection, so that I can explore family trees of people who may not be directly related to me.

#### Acceptance Criteria

1. WHEN the Family Tree View renders THEN the System SHALL display a "Search Person" button at the top of the family tree UI
2. WHEN a user clicks the "Search Person" button THEN the System SHALL open a multi-step search dialog
3. WHEN the search dialog opens THEN the System SHALL display Step 1 asking for first name, last name and gender (optional)
4. WHEN a user completes Step 1 THEN the System SHALL display Step 2 asking for address details with country (required), state (required), district (required), sub-district (optional), and locality (optional), with default values from the current user's address
5. WHEN a user completes Step 2 THEN the System SHALL display Step 3 asking for religion details with religion (required), category (required) and sub-category (optional), with default values from the current user's religion
6. WHEN a user completes Step 3 THEN the System SHALL display Step 4 showing a list of matched persons based on the search criteria. It should also show the fuzzy match score.
7. WHEN displaying matched persons in Step 4 THEN the System SHALL show each person's name, birth year, Comma seperated address, and comma seperated religion information
8. WHEN displaying each matched person THEN the System SHALL provide an "Explore" button next to each person
9. WHEN a user clicks the "Explore" button for a matched person THEN the System SHALL close the search dialog and render the family tree centered on that person
10. WHEN no persons match the search criteria THEN the System SHALL display a message indicating no results were found
11. WHEN a user navigates between steps THEN the System SHALL allow going back to previous steps to modify search criteria, Search criteria should be preserved while navigating back and forth.
12. WHEN a user closes the search dialog THEN the System SHALL return to the current family tree view without changes
