const Card = ({ children, className = '', ...props }) => (
    <div
        className={`bg-white rounded-2xl border border-gray-100 shadow-sm ${className}`}
        {...props}
    >
        {children}
    </div>
);

export const CardHeader = ({ children, className = '' }) => (
    <div className={`px-4 pt-4 pb-3 sm:px-6 sm:pt-6 sm:pb-4 ${className}`}>{children}</div>
);

export const CardContent = ({ children, className = '' }) => (
    <div className={`px-4 pb-4 sm:px-6 sm:pb-6 ${className}`}>{children}</div>
);

export default Card;