/// <reference types="cypress" />

describe('test home page', () => {
    beforeEach(() => {
        cy.visit('http://localhost:4200');
    });

    it('click something', () => {
        cy.get('#home').click();
        cy.url().should('eq', 'http://localhost:4200/');

        cy.wait(1000);
        cy.get('.mat-cell').contains('mle-lg-ref-1').click();
        cy.url().should('eq', 'http://localhost:4200/place/mle-lg-ref-1')
    });

    it('click something', () => {
        cy.get('#home').click();
        cy.url().should('eq', 'http://localhost:4200/');

        cy.wait(1000);
        cy.get('.mat-raised-button').click();
        cy.get('#mat-dialog-0');
        cy.get('#mat-input-2').click()//('CypressTest');

    });

});
