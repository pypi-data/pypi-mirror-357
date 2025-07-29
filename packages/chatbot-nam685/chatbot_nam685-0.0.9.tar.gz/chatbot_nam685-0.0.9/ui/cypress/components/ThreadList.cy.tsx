import React from 'react';
import { mount } from 'cypress/react';
import ThreadList from '../../app/components/ThreadList';
import { Thread } from '../../app/models';

describe('<ThreadList />', () => {
    it('should display thread IDs', () => {
        const mockThreads = [
            new Thread('thread-1', 'idle'),
            new Thread('thread-2', 'interrupted'),
        ];

        mount(
            <ThreadList
                threads={mockThreads}
                selectedThread={null}
                setSelectedThread={() => { }}
                deleteThread={() => { }}
            />
        );

        cy.contains('thread-1').should('be.visible');
        cy.contains('thread-2').should('be.visible');
    });
});