describe('Single Coin Page', () => {

  beforeEach(() => { 
    cy.visit('/coin/uuid-1?testing=1&fixture=coins.json')
  })

  it('displays the coin name as the page heading', () => {
    cy.get('h1').should('contain', 'Automate')
  })

  it('displays all duties associated with the coin', () => {
    const duties = ['D1 - Duty 1', 'D2 - Duty 2']

    cy.get('.grid').should('exist')
      .find('.card').should('have.length', duties.length)
      .each(($card, index) => {
        cy.wrap($card).find('a')
          .should('contain.text', duties[index])
          .and('have.attr', 'href')
          .and('include', `duties/D${index + 1}?coin_id=uuid-1`)
      })
  })

  it('shows a message if there are no duties', () => {
    cy.visit('/coin/uuid-empty-coin?testing=1')

    cy.get('.grid').should('not.exist')
    cy.get('.card').should('have.length', 0)

    cy.contains('.no-duties-message',
      'No duties associated with this coin.'
    ).should('exist')
  })

  it('shows completion badge correctly', () => {
    cy.get('.completion-badge').should('exist')
  })

  it('has a back link to the landing page', () => {
    cy.get('.back-link')
      .should('exist')
      .and('contain', 'Back to all coins')
      .click()

    cy.url().should('include', '/?testing=1')
  })

})

describe('Single Coin Page (Logged In)', () => {

  beforeEach(() => {

    cy.visit('/test-login?testing=1')

    cy.visit('/coin/uuid-1?testing=1&fixture=coins.json')
  })

  it('shows completion button when logged in', () => {

    cy.get('.completion-form button')
      .should('exist')
      .then($btn => {

        const text = $btn.text().trim()

        expect([
          'Mark Complete',
          'Mark Incomplete'
        ]).to.include(text)

      })
  })
})