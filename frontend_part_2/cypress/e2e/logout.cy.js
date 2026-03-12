describe('Logout', () => {
  beforeEach(() => {
    cy.visit('/?testing=1')
    cy.window().then((win) => {
      win.sessionStorage.setItem('username', 'test_user')
      win.sessionStorage.setItem('role', 'user')
    })
  })

  it('logs out the user and redirects to the landing page', () => {
    cy.get('form[action="/logout"] button[type="submit"]').click()

    cy.url().should('eq', 'http://localhost:8080/?testing=1')

    cy.get('.flashes .success').should('contain', 'You have been logged out.')

    cy.get('nav a').contains('Login').should('exist')

    cy.get('nav span.user-info').should('not.exist')
  })
})