describe('Admin Duties Page', () => {

  context('as an admin user', () => {
    beforeEach(() => {
      cy.visit('/?testing=1')
      cy.window().then((win) => {
        win.sessionStorage.setItem('username', 'admin_user')
        win.sessionStorage.setItem('role', 'admin')
      })

      cy.visit('/admin/duties?testing=1&fixture=duties.json')
    })

    it('shows the page title and heading', () => {
      cy.title().should('eq', 'Apprenticeship Coins')
      cy.contains('h1', 'Admin - Duties')
    })

    it('displays all duties from fixture', () => {
      const dutyCodes = ['D1', 'D2', 'D3']
      dutyCodes.forEach(code => {
        cy.contains('table td', code).should('exist')
      })

      cy.get('table tbody tr').should('have.length', dutyCodes.length)
    })

    it('has action buttons for each duty', () => {
      cy.get('table tbody tr').each(($row) => {
        cy.wrap($row).find('.edit-button').should('exist')
        cy.wrap($row).find('.delete-button').should('exist')
      })
    })

    it('links to create new duty page', () => {
      cy.get('a.create-new').should('exist').and('contain', 'Create New Duty')
    })

    it('has a back link to the coins landing page', () => {
      cy.get('a.back-link').should('exist').and('contain', 'Back to Coins').click()
      cy.url().should('eq', 'http://localhost:8080/?testing=1')
    })
  })

  context('as a non-admin user', () => {
    beforeEach(() => {
      cy.visit('/?testing=1')
      cy.window().then((win) => {
        win.sessionStorage.setItem('username', 'regular_user')
        win.sessionStorage.setItem('role', 'user')
      })
    })

    it('redirects non-admin users', () => {
      cy.visit('/admin/duties?testing=1')
      cy.url().should('eq', 'http://localhost:8080/')
      cy.get('.flashes .error').should('contain', 'Access denied')
    })
  })

  context('as a logged-out user', () => {
    it('redirects to login page', () => {
      cy.visit('/admin/duties?testing=1')
      cy.url().should('include', '/login')
    })
  })

})