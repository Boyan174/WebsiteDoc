import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import UrlInput from './components/UrlInput';
import AnalysisReport from './components/AnalysisReport';
import { analyzeUrlStream, AnalysisReportData, ProgressEventData } from './services/api';

// AnalysisReportData is now imported from api.ts

function App() {
    const [report, setReport] = useState<AnalysisReportData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [progressMessage, setProgressMessage] = useState('Initializing analysis...');
    const [progressPercent, setProgressPercent] = useState(0);
    const [currentStepName, setCurrentStepName] = useState('Initialization');

    const eventSourceRef = useRef<EventSource | null>(null);

    const handleAnalyze = async (url: string) => {
        setLoading(true);
        setError('');
        setReport(null);
        setProgressMessage('Initializing analysis...');
        setProgressPercent(0);
        setCurrentStepName('Initialization');

        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        eventSourceRef.current = analyzeUrlStream(
            url,
            (progressData: ProgressEventData) => {
                // console.log("Progress Data:", progressData);
                setProgressMessage(progressData.message);
                if (progressData.progress !== undefined) {
                    setProgressPercent(progressData.progress);
                }
                if (progressData.step_name) {
                    setCurrentStepName(progressData.step_name);
                }
                if (progressData.error) {
                    // setError(progressData.message); // Display error message from stream
                    // setLoading(false); // Stop loading on stream error if it's fatal
                    // if (eventSourceRef.current) eventSourceRef.current.close();
                    // For now, we let the loading screen show the error message from stream
                }
            },
            (finalReport: AnalysisReportData) => {
                // console.log("Final Report:", finalReport);
                setReport(finalReport);
                setLoading(false);
                setProgressMessage('Analysis complete!');
                setProgressPercent(100);
            },
            (errorMessage: string) => {
                console.error("SSE Error:", errorMessage);
                setError(errorMessage || 'An error occurred during analysis.');
                setLoading(false);
                setProgressMessage('Error occurred.');
                setProgressPercent(0); // Or keep last known progress
                if (eventSourceRef.current) eventSourceRef.current.close();
            },
            () => { // onOpen
                console.log("SSE Connection Opened by App.tsx");
                setLoading(true); // Ensure loading is true when connection opens
            },
            () => { // onClose
                console.log("SSE Connection Closed by App.tsx");
                // setLoading(false); // Might be premature if error occurs and we want to show error in loading state
                // If loading is still true and no report, it means it closed unexpectedly or with error
                if (loading && !report && !error) {
                    // setError("Connection closed unexpectedly."); // This might override specific errors
                }
            }
        );
    };

    // Cleanup useEffect for eventSource
    useEffect(() => {
        return () => {
            if (eventSourceRef.current) {
                console.log("Closing EventSource from useEffect cleanup.");
                eventSourceRef.current.close();
            }
        };
    }, []);


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
                        <p className="loading-text">{currentStepName}: {progressMessage}</p>
                        <div className="progress-bar-wrapper">
                            <div className="progress-bar-container">
                                <div 
                                    className="progress-bar" 
                                    style={{ width: `${progressPercent}%` }}
                                />
                            </div>
                            <div className="progress-percentage">
                                {progressPercent}%
                            </div>
                        </div>
                        {/* <p className="loading-steps">Current step: {currentStepName}</p> */}
                    </div>
                )}

                {error && !loading && ( // Only show general error if not loading (stream error handled in loading UI)
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
