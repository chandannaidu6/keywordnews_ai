// Button.tsx
import React from 'react';

// Define the props for the Button component
interface ButtonProps {
  onClick: () => void; // Function to handle the button click
  children: React.ReactNode; // The content of the button (text, icon, etc.)
  disabled?: boolean; // Optional: disable the button
  className?: string; // Optional: additional CSS classes
}

const Button: React.FC<ButtonProps> = ({ onClick, children, disabled = false, className = '' }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn ${className}`} // Add custom class if needed
      style={{
        padding: '10px 20px',
        fontSize: '16px',
        backgroundColor: disabled ? '#ccc' : '#007BFF',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: disabled ? 'not-allowed' : 'pointer',
      }}
    >
      {children}
    </button>
  );
};

export default Button;
