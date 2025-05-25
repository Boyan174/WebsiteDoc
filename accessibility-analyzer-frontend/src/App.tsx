import React, { useState } from 'react';
import './App.css';
import UrlInput from './components/UrlInput';
import AnalysisReport from './components/AnalysisReport';
import { analyzeUrl } from './services/api';

// Define the structure of the report data
interface AccessibilityFeedback {
  category: string;
  score: number;
  feedback: string;
}

interface AnalysisReportData {
  scores: AccessibilityFeedback[];
  implementation_plan: string;
}

function App() {
    const [report, setReport] = useState<AnalysisReportData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleAnalyze = async (url: string) => {
        setLoading(true);
        setError('');
        setReport(null);
        try {
            const result = await analyzeUrl(url);
            setReport(result);
        } catch (err) {
            setError('Failed to analyze the URL. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <div className="container">
                <header className="header">
                    <h1>AccessDoc AI</h1>
                    <p>Let our AI Agent analyze your website's accessibility for you!</p>
                </header>

                <div className="url-input-section">
                    <UrlInput onAnalyze={handleAnalyze} loading={loading} />
                </div>

                {loading && (
                    <div className="loading-container fade-in">
                        <div className="loading-spinner"></div>
                        <p className="loading-text">Analyzing website accessibility...</p>
                        <p className="loading-steps">Capturing screenshot • Extracting HTML • Generating report</p>
                    </div>
                )}

                {error && (
                    <div className="error-container fade-in">
                        <svg className="error-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <p className="error-text">{error}</p>
                    </div>
                )}

                {report && !loading && (
                    <div className="fade-in">
                        <AnalysisReport report={report} />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
