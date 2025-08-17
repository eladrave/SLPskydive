import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import HomePage from './HomePage';

describe('HomePage', () => {
    it('renders the main heading', () => {
        render(
            <MemoryRouter>
                <HomePage />
            </MemoryRouter>
        );
        const heading = screen.getByText(/Welcome to the Skydiving Scheduler/i);
        expect(heading).toBeInTheDocument();
    });
});
