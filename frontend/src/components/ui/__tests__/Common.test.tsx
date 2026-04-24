import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Card, Tag } from '../Common';

describe('Card Component', () => {
  test('renders card with children', () => {
    render(
      <Card>
        <div>Card Content</div>
      </Card>
    );

    expect(screen.getByText('Card Content')).toBeInTheDocument();
  });

  test('applies custom className', () => {
    const { container } = render(
      <Card className="custom-class">
        <div>Card Content</div>
      </Card>
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  test('handles click event', () => {
    const handleClick = jest.fn();
    render(
      <Card onClick={handleClick}>
        <div>Clickable Card</div>
      </Card>
    );

    fireEvent.click(screen.getByText('Clickable Card'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

describe('Tag Component', () => {
  test('renders tag with default variant', () => {
    render(<Tag>Default Tag</Tag>);
    expect(screen.getByText('Default Tag')).toBeInTheDocument();
  });

  test('renders tag with different variants', () => {
    const { rerender } = render(<Tag variant="success">Success Tag</Tag>);
    expect(screen.getByText('Success Tag')).toBeInTheDocument();

    rerender(<Tag variant="warning">Warning Tag</Tag>);
    expect(screen.getByText('Warning Tag')).toBeInTheDocument();
  });

  test('applies custom className', () => {
    const { container } = render(
      <Tag className="custom-tag">Custom Tag</Tag>
    );

    expect(container.firstChild).toHaveClass('custom-tag');
  });

  test('handles click event', () => {
    const handleClick = jest.fn();
    render(
      <Tag onClick={handleClick}>
        Clickable Tag
      </Tag>
    );

    fireEvent.click(screen.getByText('Clickable Tag'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});