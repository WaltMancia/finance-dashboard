const Spinner = ({ size = 'md', className = '' }) => {
    const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' };
    return (
        <div className={`${sizes[size]} border-4 border-gray-100
      border-t-gray-900 rounded-full animate-spin ${className}`}
        />
    );
};
export default Spinner;