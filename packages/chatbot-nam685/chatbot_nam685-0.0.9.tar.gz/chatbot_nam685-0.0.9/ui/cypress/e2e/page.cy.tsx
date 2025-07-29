describe('Page Title', () => {
    it('should display the correct page title', () => {
        // Visit the home page
        cy.visit('http://localhost:3000/');

        // Check if the page contains an h1 with the text "Chatbot"
        cy.get('h1').should('contain', 'Chatbot');
    });
});