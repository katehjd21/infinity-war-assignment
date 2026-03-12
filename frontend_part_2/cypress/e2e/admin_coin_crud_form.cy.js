describe('Admin Coin CRUD Form Page', () => {

  const coinName = "Test Coin"
  const dutyCodes = "D1,D2"
  const coinId = "uuid-1"

  const setAdminSession = () => {
    cy.window().then((win) => {
      win.sessionStorage.setItem('username', 'admin_user')
      win.sessionStorage.setItem('role', 'admin')
    })
  }

  context('Create Coin', () => {
    beforeEach(() => {
      cy.visit('/admin/coins/create?testing=1&fixture=coins.json', { failOnStatusCode: false })
      setAdminSession()
    })

    it('displays the create form', () => {
      cy.contains('h1', 'Create Coin').should('exist')
      cy.get('input#name').should('exist')
      cy.get('input#duty_codes').should('exist')
      cy.get('input#completed').should('exist')
      cy.get('button.save-button').should('exist')
    })

    it('can create a coin successfully', () => {
      cy.get('input#name').type(coinName)
      cy.get('input#duty_codes').type(dutyCodes)
      cy.get('input#completed').check()

      cy.intercept('POST', '/admin/coins/create', (req) => {
        req.reply((res) => {
          res.redirect('/admin/coins')
        })
      }).as('createCoin')

      cy.get('button.save-button').click()
      cy.wait('@createCoin')

      cy.url().should('include', '/admin/coins')
      cy.contains('.flashes .success', 'Coin created successfully.').should('exist')
    })
  })

  context('Edit Coin', () => {
    beforeEach(() => {
      cy.visit(`/admin/coins/${coinId}/edit?testing=1&fixture=coins.json`, { failOnStatusCode: false })
      setAdminSession()
    })

    it('displays the edit form pre-filled', () => {
      cy.contains('h1', 'Edit Coin').should('exist')
      cy.get('input#name').should('have.value', 'Automate')
      cy.get('input#duty_codes').should('have.value', 'D1,D2')
      cy.get('input#completed').should('be.checked')
    })
  })

  context('Delete Coin', () => {
    it('can delete a coin successfully', () => {
      cy.visit(`/admin/coins?testing=1&fixture=coins.json`, { failOnStatusCode: false })
      setAdminSession()

      cy.intercept('POST', `/admin/coins/${coinId}/delete`, {
        statusCode: 302,
        headers: { location: '/admin/coins' }
      }).as('deleteCoin')

      cy.get(`form[action="/admin/coins/${coinId}/delete"] button`).click()
      cy.wait('@deleteCoin')

      cy.url().should('include', '/admin/coins')
      cy.contains('.flashes .success', 'Coin deleted successfully.').should('exist')
    })
  })
})