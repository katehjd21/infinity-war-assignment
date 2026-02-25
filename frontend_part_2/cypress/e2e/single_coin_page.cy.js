describe('Single Coin Page', () => {
  beforeEach(() => { 
    cy.visit('/coin/uuid-1?testing=1')
  })

  it('displays the coin name as the page heading', () => {
    cy.get('h1').should('contain', 'Automate')
  })

  it('displays all duties associated with the coin', () => {
    const duties = ['D1 - Duty 1', 'D2 - Duty 2']
    duties.forEach(dutyText => {
      cy.contains('.card a', dutyText).should('exist')
    })
    cy.get('.card').should('have.length', duties.length)
  })

  it('shows a message if there are no duties', () => {
  cy.visit('/coin/uuid-empty-coin?testing=1')
  cy.get('.card').should('have.length', 0)
  cy.contains('.muted', 'No duties associated with this coin.').should('exist')
  })

  it('has a back link to the landing page', () => {
  cy.get('.back-link')
    .should('exist')
    .and('contain', 'Back to all coins')
    .click()

  cy.url().should('eq', 'http://localhost:8080/?testing=1')
  })
})