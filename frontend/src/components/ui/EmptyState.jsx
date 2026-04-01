const EmptyState = ({ icon, title, description, action }) => (
    <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="text-5xl mb-4">{icon}</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        {description && (
            <p className="text-gray-500 mb-6 max-w-sm text-sm">{description}</p>
        )}
        {action}
    </div>
);

export default EmptyState;