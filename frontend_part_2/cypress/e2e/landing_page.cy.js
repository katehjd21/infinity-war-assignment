describe('Landing Page', () => {
  beforeEach(() => {
    cy.visit('/?testing=1&fixture=coins.json')
  })

  it('has a page title and a heading', () => {
    cy.title().should('eq', 'Apprenticeship Coins')
    cy.contains('h1', 'Apprenticeship Coins')
  })

  it('displays all coins from the fixture', () => {
    const coinNames = ['Automate', 'Houston', 'Security', 'Going Deeper', 'Assemble', 'Empty Coin']
    coinNames.forEach(name => {
      cy.contains('.card a', name).should('exist')
    })

    cy.get('.card').should('have.length', coinNames.length)
  })

  it('navigates to a single coin page when a coin is clicked', () => {
    cy.contains('.card a', 'Automate').click()
    cy.url().should('include', '/coin/uuid-1?testing=1')
    cy.get('h1').should('exist')
  })

  it('handles empty coin list gracefully', () => {
  cy.visit('/?testing=1&fixture=empty_coins.json')

  cy.get('.card').should('have.length', 0)
  cy.contains('.no-coins-message', 'No Coins Available').should('exist')
})
})