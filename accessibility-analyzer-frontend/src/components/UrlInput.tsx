import React, { useState } from 'react';

interface UrlInputProps {
    onAnalyze: (url: string) => void;
    loading?: boolean;
}

const UrlInput: React.FC<UrlInputProps> = ({ onAnalyze, loading = false }) => {
    const [url, setUrl] = useState('');
    const [isValid, setIsValid] = useState(true);

    const validateUrl = (url: string) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (validateUrl(url)) {
            setIsValid(true);
            onAnalyze(url);
        } else {
            setIsValid(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUrl(e.target.value);
        if (!isValid && e.target.value) {
            setIsValid(validateUrl(e.target.value));
        }
    };

    return (
        <form onSubmit={handleSubmit} className="url-form">
            <div className="url-input-wrapper">
                <svg className="url-input-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
                </svg>
                <input
                    type="text"
                    value={url}
                    onChange={handleInputChange}
                    placeholder="Enter website URL (e.g., https://example.com)"
                    required
                    className={`url-input ${!isValid ? 'error' : ''}`}
                    disabled={loading}
                />
                {!isValid && (
                    <p style={{ color: 'var(--danger-color)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        Please enter a valid URL
                    </p>
                )}
            </div>
            <button type="submit" className="analyze-button" disabled={loading || !url}>
                {loading ? (
                    <>
                        <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Analyzing...
                    </>
                ) : (
                    <>
                        <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                            <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                        </svg>
                        Analyze
                    </>
                )}
            </button>
        </form>
    );
};

export default UrlInput;
