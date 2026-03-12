describe('Admin Logs Page', () => {

  const logsFixture = [
    { method: "GET", path: "/login", user: "user1", timestamp: "2026-03-05T10:00:00Z" },
    { method: "POST", path: "/coin/1", user: "user2", timestamp: "2026-03-05T11:00:00Z" }
  ];

  beforeEach(() => {
    cy.window().then((win) => {
      win.sessionStorage.setItem('username', 'admin_user')
      win.sessionStorage.setItem('role', 'admin')
    })

    cy.visit('/admin/logs?testing=1&fixture=logs.json')
  })

  it('renders page title and heading', () => {
    cy.title().should('eq', 'Admin Logs')
    cy.contains('h1', 'Last 100 HTTP Requests')
  })

  it('displays logs from fixture', () => {
    cy.intercept('GET', '/admin/logs', {
      statusCode: 200,
      body: logsFixture
    }).as('getLogs')

    cy.visit('/admin/logs?testing=1')
    cy.wait('@getLogs')

    cy.get('table thead tr').within(() => {
      cy.contains('Method').should('exist')
      cy.contains('Path').should('exist')
      cy.contains('User').should('exist')
      cy.contains('Timestamp').should('exist')
    })

    cy.get('table tbody tr').should('have.length', logsFixture.length)

    logsFixture.forEach((log, index) => {
      cy.get(`table tbody tr:eq(${index})`).within(() => {
        cy.contains(log.method)
        cy.contains(log.path)
        cy.contains(log.user)
        cy.contains(log.timestamp.replace('T', ' ').substring(0, 19))
      })
    })
  })

  it('handles empty logs gracefully', () => {
    cy.intercept('GET', '/admin/logs', {
      statusCode: 200,
      body: []
    }).as('getEmptyLogs')

    cy.visit('/admin/logs?testing=1')
    cy.wait('@getEmptyLogs')

    cy.get('table tbody tr').should('have.length', 0)
    cy.contains('.back-link', 'Back to Home').should('exist')
  })

  it('back link navigates to landing page', () => {
    cy.get('.back-link')
      .should('exist')
      .and('contain', 'Back to Home')
      .click()

    cy.url().should('eq', 'http://localhost:8080/')
  })

  it('shows flash error if backend fails', () => {
    cy.intercept('GET', '/admin/logs', {
      statusCode: 500
    }).as('getLogsFail')

    cy.visit('/admin/logs?testing=1')
    cy.wait('@getLogsFail')

    cy.contains('.flashes .error', 'Could not load logs from backend.').should('exist')
  })
})