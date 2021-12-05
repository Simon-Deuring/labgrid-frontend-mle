/// <reference types="cypress" />


describe('navigation tests', () => {


  it('should display the home page', () => {
    cy.visit('/'); // go to the home page

    cy.get('[id="home"]').click();
    cy.url().should('eq', 'http://localhost:4200/');


    cy.visit('/place/mle-lg-ref-1');

    cy.get('[id="home"]').click();
    cy.url().should('eq', 'http://localhost:4200/');

  });

})
