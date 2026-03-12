describe('Admin Coins Page', () => {

  context('as an admin user', () => {
    beforeEach(() => {
      cy.visit('/?testing=1')
      cy.window().then((win) => {
        win.sessionStorage.setItem('username', 'admin_user')
        win.sessionStorage.setItem('role', 'admin')
      })

      cy.visit('/admin/coins?testing=1&fixture=coins.json')
    })

    it('shows the page title and heading', () => {
      cy.title().should('eq', 'Apprenticeship Coins')
      cy.contains('h1', 'Admin - Coins')
    })

    it('displays all coins from fixture', () => {
      const coinNames = ['Automate', 'Houston', 'Security', 'Going Deeper', 'Assemble', 'Empty Coin']
      coinNames.forEach(name => {
        cy.contains('table td', name).should('exist')
      })

      cy.get('table tbody tr').should('have.length', coinNames.length)
    })

    it('has action buttons for each coin', () => {
      cy.get('table tbody tr').each(($row) => {
        cy.wrap($row).find('.edit-button').should('exist')
        cy.wrap($row).find('.delete-button').should('exist')
      })
    })

    it('links to create new coin page', () => {
      cy.get('a.create-new').should('exist').and('contain', 'Create New Coin')
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
      cy.visit('/admin/coins?testing=1')
      cy.url().should('eq', 'http://localhost:8080/')
      cy.get('.flashes .error').should('contain', 'Access denied')
    })
  })

  context('as a logged-out user', () => {
    it('redirects to login page', () => {
      cy.visit('/admin/coins?testing=1')
      cy.url().should('include', '/login')
    })
  })

})