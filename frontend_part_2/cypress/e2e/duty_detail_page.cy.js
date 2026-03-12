describe('Duty Detail Page', () => {
  beforeEach(() => {
    cy.visit('/duties/D1?coin_id=uuid-1&testing=1')
  })

  it('displays the duty code and name as heading', () => {
    cy.get('h1').should('contain', 'D1 - Duty 1')
  })

  it('displays the duty description', () => {
    cy.contains('h2', 'Description').should('exist')
    cy.get('.description-box').should('contain', 'Duty 1 Description')
  })

  it('displays all coins associated with the duty', () => {
    const coins = ['Automate', 'Houston']
    const coinIds = ['uuid-1', 'uuid-2']

    cy.get('.grid .card a').should('have.length', coins.length)
      .each(($link, index) => {
        cy.wrap($link)
          .should('contain.text', coins[index])
          .and('have.attr', 'href')
          .and('include', `coin/${coinIds[index]}?testing=1`)
      });
  })

  it('shows empty-state message if no coins are associated', () => {
    cy.visit('/duties/uuid-empty-duty?coin_id=uuid-1&testing=1')
    cy.get('.grid').should('not.exist')
    cy.get('.card').should('have.length', 0)
    cy.contains('.muted', 'No coins associated with this duty.').should('exist')
  })

  it('displays KSB codes if present', () => {
    const ksbs = ['K1', 'S1', 'B1']
    cy.get('.ksb-grid').should('exist')
      .find('.ksb-card').should('have.length', ksbs.length)
      .each(($card, index) => {
        cy.wrap($card).should('contain.text', ksbs[index])
      });
  })

  it('shows empty-state message if no KSB codes', () => {
    cy.visit('/duties/uuid-empty-duty?coin_id=uuid-1&testing=1')
    cy.get('.ksb-grid').should('not.exist')
    cy.contains('.muted', 'No KSB codes for this duty.').should('exist')
  })

  it('has a back link to the coin page', () => {
    cy.get('.back-button.secondary')
      .should('exist')
      .and('contain', '← Back to coin')
      .click()
    cy.url().should('include', '/coin/uuid-1?testing=1')
  })

  it('has a back link to the landing page', () => {
    cy.get('.back-button.primary')
      .should('exist')
      .and('contain', 'Back to all coins')
      .click()
    cy.url().should('eq', 'http://localhost:8080/?testing=1')
  })
})