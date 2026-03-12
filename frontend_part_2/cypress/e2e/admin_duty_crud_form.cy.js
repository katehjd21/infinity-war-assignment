describe('Admin Duty Form Page', () => {

  const dutyCode = "D99"
  const dutyName = "Test Duty"
  const dutyDescription = "Test Description"
  const ksbCodes = "KSB1,KSB2"

  context('Create Duty', () => {
    beforeEach(() => {
      cy.visit('/admin/duties/create?testing=1&fixture=coins.json')
      cy.window().then((win) => {
        win.sessionStorage.setItem('username', 'admin_user')
        win.sessionStorage.setItem('role', 'admin')
      })
    })

    it('displays the create form', () => {
      cy.contains('h1', 'Create Duty').should('exist')
      cy.get('input#code').should('exist')
      cy.get('input#name').should('exist')
      cy.get('textarea#description').should('exist')
      cy.get('.coin-checkboxes input[type="checkbox"]').should('exist')
      cy.get('input#ksb_codes').should('exist')
      cy.get('button.save-button').should('exist')
    })

    it('can create a duty successfully', () => {
      cy.get('input#code').type(dutyCode)
      cy.get('input#name').type(dutyName)
      cy.get('textarea#description').type(dutyDescription)
      cy.get('.coin-checkboxes input[type="checkbox"]').first().check()
      cy.get('input#ksb_codes').type(ksbCodes)

      cy.intercept('POST', '/admin/duties/create', (req) => {
        req.reply((res) => {
          res.redirect('/admin/duties')
        })
      }).as('createDuty')

      cy.get('button.save-button').click()
      cy.wait('@createDuty')

      cy.url().should('include', '/admin/duties')
      cy.contains('.flashes .success', 'Duty created successfully.').should('exist')
    })

    it('shows error if creation fails', () => {
      cy.get('input#code').type(dutyCode)

      cy.intercept('POST', '/admin/duties/create', {
        statusCode: 200,
        body: `<div class="error">Failed to create duty</div>`
      }).as('createFail')

      cy.get('button.save-button').click()
      cy.wait('@createFail')

      cy.contains('.error', 'Failed to create duty').should('exist')
    })
  })

  context('Edit Duty', () => {
    const dutyCode = "D1"

    beforeEach(() => {
      cy.visit(`/admin/duties/${dutyCode}/edit?testing=1&fixture=coins.json`)
      cy.window().then((win) => {
        win.sessionStorage.setItem('username', 'admin_user')
        win.sessionStorage.setItem('role', 'admin')
      })
    })

    it('displays the edit form pre-filled', () => {
      cy.contains('h1', 'Edit Duty').should('exist')
      cy.get('input#code').should('have.value', dutyCode)
      cy.get('input#name').should('have.value', 'Duty 1')
      cy.get('textarea#description').should('contain.value', 'Duty 1 Description')
      cy.get('input#ksb_codes').should('have.value', 'KSB1,KSB2')
    })

    it('can edit a duty successfully', () => {
      cy.get('input#name').clear().type('Updated Duty')
      cy.get('textarea#description').clear().type('Updated Description')
      cy.get('input#ksb_codes').clear().type('KSB3,KSB4')
      cy.get('.coin-checkboxes input[type="checkbox"]').first().uncheck()

      cy.intercept('POST', `/admin/duties/${dutyCode}/edit`, (req) => {
        req.reply((res) => {
          res.redirect('/admin/duties')
        })
      }).as('updateDuty')

      cy.get('button.save-button').click()
      cy.wait('@updateDuty')

      cy.url().should('include', '/admin/duties')
      cy.contains('.flashes .success', 'Duty updated successfully.').should('exist')
    })

    it('shows error if update fails', () => {
      cy.get('input#name').clear().type('Fail Duty')

      cy.intercept('POST', `/admin/duties/${dutyCode}/edit`, {
        statusCode: 200,
        body: `<div class="error">Failed to update duty</div>`
      }).as('updateFail')

      cy.get('button.save-button').click()
      cy.wait('@updateFail')

      cy.contains('.error', 'Failed to update duty').should('exist')
    })
  })

  context('Delete Duty', () => {
    const dutyCode = "D1"

    it('can delete a duty successfully', () => {
      cy.visit('/admin/duties?testing=1&fixture=coins.json')
      cy.window().then((win) => {
        win.sessionStorage.setItem('username', 'admin_user')
        win.sessionStorage.setItem('role', 'admin')
      })

      cy.intercept('POST', `/admin/duties/${dutyCode}/delete`, {
        statusCode: 302,
        headers: { location: '/admin/duties' }
      }).as('deleteDuty')

      cy.get(`form[action="/admin/duties/${dutyCode}/delete"] button`).click()
      cy.wait('@deleteDuty')

      cy.url().should('include', '/admin/duties')
      cy.contains('.flashes .success', 'Duty deleted successfully.').should('exist')
    })
  })
})