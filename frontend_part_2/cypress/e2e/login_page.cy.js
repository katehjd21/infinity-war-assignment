describe('Login Page', () => {
  beforeEach(() => {
    cy.visit('/login?testing=1', { failOnStatusCode: false })
  })

  it('renders the login page correctly', () => {
    cy.title().should('eq', 'Login')
    cy.contains('h1', 'Login').should('exist')
    cy.get('form').should('exist')
    cy.get('input#username').should('exist')
    cy.get('input#password').should('exist')
    cy.get('button[type="submit"]').should('contain', 'Login')
  })

  it('shows an error for invalid username/password format', () => {
    cy.get('input#username').type('!!invalid')
    cy.get('input#password').type('short')
    cy.get('button[type="submit"]').first().click()

    cy.url().should('include', '/login')
    cy.get('.flashes .error')
      .should('contain', 'Invalid username or password format.')
  })

  it('shows an error for invalid credentials', () => {
    cy.get('input#username').type('wrong_user')
    cy.get('input#password').type('wrong_password')
    cy.get('button[type="submit"]').first().click()

    cy.url().should('include', '/login')
    cy.get('.error-message').should('contain', 'Invalid credentials')
  })

  it('shows a server error message if login API fails', () => {
    // Simulate server error via URL param in testing mode
    cy.visit('/login?testing=1&error=server', { failOnStatusCode: false })
    cy.get('input#username').type('any_user')
    cy.get('input#password').type('any_pass')
    cy.get('button[type="submit"]').first().click()

    cy.get('.error-message').should('contain', 'Server error. Try again later.')
  })
})

// Logged-in tests
describe('Login Page (logged-in tests)', () => {
  beforeEach(() => {
    // Pre-login using /test-login for session
    cy.request('/test-login?testing=1&role=user').then(() => {
      cy.visit('/?testing=1', { failOnStatusCode: false })
    })
  })

  it('logs in successfully with valid credentials', () => {
    cy.visit('/login?testing=1', { failOnStatusCode: false })
    cy.get('input#username').type('valid_user')
    cy.get('input#password').type('valid_password')
    cy.get('button[type="submit"]').first().click()

    // Should redirect to landing page
    cy.url().should('include', '/?testing=1')
    cy.get('.flashes .success').should('contain', 'Logged in successfully.')
  })
})