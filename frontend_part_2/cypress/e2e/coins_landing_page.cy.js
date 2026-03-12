describe('Coins Landing Page', () => {
  const coinNames = ['Automate', 'Houston', 'Security', 'Going Deeper', 'Assemble', 'Empty Coin'];

  beforeEach(() => {
    cy.visit('/?testing=1&fixture=coins.json');
  });

  it('has a page title and heading', () => {
    cy.title().should('eq', 'Apprenticeship Coins');
    cy.contains('h1', 'Apprenticeship Coins');
  });

  it('displays all coins from the fixture', () => {
    cy.get('.card').should('have.length', coinNames.length)
      .each(($card, index) => {
        cy.wrap($card).find('a').should('contain.text', coinNames[index]);
      });
  });

  it('links to correct coin page', () => {
    cy.get('.card a')
      .contains('Automate')
      .should('have.attr', 'href')
      .and('include', 'coin/uuid-1?testing=1');

    cy.contains('.card a', 'Automate').click();
    cy.url().should('include', '/coin/uuid-1?testing=1');
    cy.get('h1').should('exist');
  });

  it('handles empty coin list gracefully', () => {
    cy.visit('/?testing=1&fixture=empty_coins.json');
    cy.get('.grid').should('not.exist');
    cy.get('.card').should('have.length', 0);
    cy.contains('.no-coins-message', 'No Coins Available').should('exist');
  });
});