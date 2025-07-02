module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'angel-blue-50': '#e0f2fe', // Very light blue
        'angel-blue-100': '#bfdbfe', // Light blue
        'angel-blue-500': '#3b82f6', // Primary blue
        'angel-blue-600': '#2563eb', // Slightly darker primary blue
        'angel-blue-700': '#1d4ed8', // Darker blue
        'angel-green-500': '#22c55e', // Primary green
        'angel-green-600': '#16a34a', // Darker green
        'angel-teal': '#20B2AA', // Teal color
        'violet-50': '#f5f3ff',
        'violet-100': '#ede9fe',
        'violet-500': '#8b5cf6',
        'violet-600': '#7c3aed',
        'violet-700': '#6d28d9',
        'angel-gray-50': '#f9fafb', // Very light gray background
        'angel-gray-100': '#f3f4f6', // Light gray background
        'angel-gray-200': '#e5e7eb', // Border gray
        'angel-gray-300': '#d1d5db', // Another border gray
        'angel-gray-500': '#6b7280', // Text gray
        'angel-gray-700': '#374151', // Darker text gray
        'angel-gray-800': '#1f2937', // Heading/darkest gray
      },
    },
  },
  plugins: [],
}; 