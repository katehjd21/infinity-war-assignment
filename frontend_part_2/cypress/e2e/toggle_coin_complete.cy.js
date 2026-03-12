describe('Toggle Coin Completion', () => {

  const coinId = 'uuid-1'

  beforeEach(() => {
    cy.window().then((win) => {
      win.sessionStorage.setItem('username', 'test_user')
    })
  })

  it('shows correct initial completion state', () => {
    cy.visit(`/coin/${coinId}?testing=1&fixture=coins.json`)
    cy.get('.completion-badge').then($badge => {
      const text = $badge.text().trim()
      cy.get('.completion-form button').should('contain', text.includes('Completed') ? 'Mark Incomplete' : 'Mark Complete')
    })
  })

  it('toggles completion state when clicked', () => {
    cy.intercept('POST', '/toggle_coin_complete', (req) => {
      req.reply({
        statusCode: 200,
        body: { completed: true }
      })
    }).as('toggleComplete')

    cy.visit(`/coin/${coinId}?testing=1&fixture=coins.json`)

    cy.get('.completion-form button').then($btn => {
      const initialText = $btn.text().trim()
      cy.wrap($btn).click()
      cy.wait('@toggleComplete')

      cy.get('.completion-form button').should('not.have.text', initialText)
      cy.get('.completion-badge').should('contain', initialText.includes('Completed') ? 'In Progress' : 'Coin Completed')
    })
  })
})