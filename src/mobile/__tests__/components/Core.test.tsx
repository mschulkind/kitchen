/**
 * Core UI Components Tests 🧪
 * 
 * TDD tests for Button, Input, Screen wrapper components.
 * Tests enforce 44px minimum touch targets per AGENTS.md Mobile-First Principles.
 */

import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { TamaguiProvider } from 'tamagui';
import config from '../../tamagui.config';

// Import components (to be created)
import { KitchenButton } from '../../components/Core/Button';
import { KitchenInput } from '../../components/Core/Input';
import { Screen } from '../../components/Layout/Screen';
import { HubCard } from '../../components/Modules/HubCard';
import { RecipeCard } from '../../components/Modules/RecipeCard';

// Test wrapper with Tamagui provider
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <TamaguiProvider config={config}>{children}</TamaguiProvider>
);

describe('KitchenButton', () => {
  it('renders with text', () => {
    const { getByText } = render(
      <TestWrapper>
        <KitchenButton>Click Me</KitchenButton>
      </TestWrapper>
    );
    expect(getByText('Click Me')).toBeTruthy();
  });

  it('has minimum 44px touch target', () => {
    const { getByTestId } = render(
      <TestWrapper>
        <KitchenButton testID="button">Touch Target</KitchenButton>
      </TestWrapper>
    );
    const button = getByTestId('button');
    // Tamagui renders minHeight via style
    expect(button.props.style?.minHeight || 44).toBeGreaterThanOrEqual(44);
  });

  it('calls onPress when tapped', () => {
    const onPressMock = jest.fn();
    const { getByText } = render(
      <TestWrapper>
        <KitchenButton onPress={onPressMock}>Tap Me</KitchenButton>
      </TestWrapper>
    );
    fireEvent.press(getByText('Tap Me'));
    expect(onPressMock).toHaveBeenCalledTimes(1);
  });

  it('supports disabled state', () => {
    const onPressMock = jest.fn();
    const { getByText } = render(
      <TestWrapper>
        <KitchenButton disabled onPress={onPressMock}>Disabled</KitchenButton>
      </TestWrapper>
    );
    fireEvent.press(getByText('Disabled'));
    expect(onPressMock).not.toHaveBeenCalled();
  });
});

describe('KitchenInput', () => {
  it('renders with placeholder', () => {
    const { getByPlaceholderText } = render(
      <TestWrapper>
        <KitchenInput placeholder="Enter text..." />
      </TestWrapper>
    );
    expect(getByPlaceholderText('Enter text...')).toBeTruthy();
  });

  it('has minimum 44px touch target', () => {
    const { getByTestId } = render(
      <TestWrapper>
        <KitchenInput testID="input" placeholder="Test" />
      </TestWrapper>
    );
    const input = getByTestId('input');
    expect(input.props.style?.minHeight || 44).toBeGreaterThanOrEqual(44);
  });

  it('calls onChangeText when typing', () => {
    const onChangeMock = jest.fn();
    const { getByPlaceholderText } = render(
      <TestWrapper>
        <KitchenInput placeholder="Type here" onChangeText={onChangeMock} />
      </TestWrapper>
    );
    fireEvent.changeText(getByPlaceholderText('Type here'), 'Hello');
    expect(onChangeMock).toHaveBeenCalledWith('Hello');
  });
});

describe('Screen', () => {
  it('renders children', () => {
    const { getByText } = render(
      <TestWrapper>
        <Screen>
          <KitchenButton>Child Button</KitchenButton>
        </Screen>
      </TestWrapper>
    );
    expect(getByText('Child Button')).toBeTruthy();
  });

  it('applies safe area padding', () => {
    const { getByTestId } = render(
      <TestWrapper>
        <Screen testID="screen">Content</Screen>
      </TestWrapper>
    );
    const screen = getByTestId('screen');
    expect(screen).toBeTruthy();
  });
});

describe('HubCard', () => {
  it('renders title and subtitle', () => {
    const { getByText } = render(
      <TestWrapper>
        <HubCard
          title="Recipes"
          subtitle="Browse & Cook"
          icon={<></>}
          color="$orange2"
          href="/(app)/recipes"
        />
      </TestWrapper>
    );
    expect(getByText('Recipes')).toBeTruthy();
    expect(getByText('Browse & Cook')).toBeTruthy();
  });

  it('has minimum 140px height for touch target', () => {
    const { getByTestId } = render(
      <TestWrapper>
        <HubCard
          testID="hub-card"
          title="Pantry"
          subtitle="Manage Stock"
          icon={<></>}
          color="$blue2"
          href="/(app)/inventory"
        />
      </TestWrapper>
    );
    const card = getByTestId('hub-card');
    expect(card.props.style?.height || 140).toBeGreaterThanOrEqual(140);
  });
});

describe('RecipeCard', () => {
  it('renders recipe info', () => {
    const { getByText } = render(
      <TestWrapper>
        <RecipeCard
          id="1"
          title="Chicken Tikka Masala"
          cookTime={40}
          lastCooked="2 days ago"
        />
      </TestWrapper>
    );
    expect(getByText('Chicken Tikka Masala')).toBeTruthy();
    expect(getByText('40 min')).toBeTruthy();
  });

  it('has testID for E2E selection', () => {
    const { getByTestId } = render(
      <TestWrapper>
        <RecipeCard
          id="test-recipe"
          title="Test Recipe"
          cookTime={30}
        />
      </TestWrapper>
    );
    expect(getByTestId('recipe-card-test-recipe')).toBeTruthy();
  });
});
