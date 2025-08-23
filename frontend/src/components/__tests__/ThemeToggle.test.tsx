import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '../../contexts/ThemeContext';
import ThemeToggle from '../ThemeToggle';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockReturnValue('dark');
    localStorageMock.setItem.mockClear();
  });

  const renderWithTheme = (component: React.ReactElement) => {
    return render(
      <ThemeProvider>
        {component}
      </ThemeProvider>
    );
  };

  test('renders theme toggle button', () => {
    renderWithTheme(<ThemeToggle />);
    const toggleButton = screen.getByRole('button', { name: /switch to light mode/i });
    expect(toggleButton).toBeInTheDocument();
  });

  test('toggles theme when clicked', () => {
    renderWithTheme(<ThemeToggle />);
    const toggleButton = screen.getByRole('button', { name: /switch to light mode/i });
    
    // Initially should be dark mode
    expect(toggleButton).toHaveAttribute('aria-label', 'Switch to light mode');
    
    // Click to toggle to light mode
    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute('aria-label', 'Switch to dark mode');
    
    // Click again to toggle back to dark mode
    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute('aria-label', 'Switch to light mode');
  });

  test('saves theme preference to localStorage', () => {
    renderWithTheme(<ThemeToggle />);
    const toggleButton = screen.getByRole('button');
    
    fireEvent.click(toggleButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
  });

  test('loads theme preference from localStorage on mount', () => {
    localStorageMock.getItem.mockReturnValue('light');
    renderWithTheme(<ThemeToggle />);
    
    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toHaveAttribute('aria-label', 'Switch to dark mode');
  });

  test('defaults to dark mode when no preference is stored', () => {
    localStorageMock.getItem.mockReturnValue(null);
    renderWithTheme(<ThemeToggle />);
    
    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toHaveAttribute('aria-label', 'Switch to light mode');
  });
});
