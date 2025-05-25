import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface AccessibilityFeedback {
    category: string;
    score: number;
    feedback: string;
}

interface AnalysisReportData {
    scores: AccessibilityFeedback[];
    implementation_plan: string;
}

interface AnalysisReportProps {
    report: AnalysisReportData | null;
}

const AnalysisReport: React.FC<AnalysisReportProps> = ({ report }) => {
    const [copiedToClipboard, setCopiedToClipboard] = useState(false);

    if (!report) return null;

    const getScoreClass = (score: number) => {
        if (score >= 90) return 'excellent';
        if (score >= 70) return 'good';
        if (score >= 50) return 'needs-improvement';
        return 'poor';
    };

    const getScoreEmoji = (score: number) => {
        if (score >= 90) return '✅';
        if (score >= 70) return '👍';
        if (score >= 50) return '⚠️';
        return '❌';
    };

    const downloadReport = () => {
        const reportString = `Accessibility Analysis Report
=============================

Overall Scores:
${report.scores.map(item => `
${item.category}: ${item.score}/100 ${getScoreEmoji(item.score)}
Feedback: ${item.feedback}
`).join('\n')}

Implementation Plan:
--------------------
${report.implementation_plan}

Generated on: ${new Date().toLocaleString()}
`;
        const blob = new Blob([reportString], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `accessibility-report-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const copyToClipboard = async () => {
        const reportString = `Accessibility Analysis Report

Overall Scores:
${report.scores.map(item => `${item.category}: ${item.score}/100 - ${item.feedback}`).join('\n')}

Implementation Plan:
${report.implementation_plan}`;

        try {
            await navigator.clipboard.writeText(reportString);
            setCopiedToClipboard(true);
            setTimeout(() => setCopiedToClipboard(false), 2000);
        } catch (err) {
            console.error('Failed to copy to clipboard:', err);
        }
    };

    const averageScore = Math.round(
        report.scores.reduce((sum, item) => sum + item.score, 0) / report.scores.length
    );

    return (
        <div className="report-container">
            <div className="report-header">
                <div>
                    <h2>Accessibility Report</h2>
                    <p style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.25rem' }}>
                        Average Score: {averageScore}/100 {getScoreEmoji(averageScore)}
                    </p>
                </div>
                <div className="report-actions">
                    <button onClick={copyToClipboard} className="report-action-button">
                        {copiedToClipboard ? (
                            <>
                                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Copied!
                            </>
                        ) : (
                            <>
                                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                                    <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                                </svg>
                                Copy
                            </>
                        )}
                    </button>
                    <button onClick={downloadReport} className="report-action-button">
                        <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                        Download
                    </button>
                </div>
            </div>

            <div className="scores-grid">
                {report.scores.map((item, index) => (
                    <div key={index} className="score-card">
                        <div className="score-card-header">
                            <h3 className="score-card-title">{item.category}</h3>
                            <div className={`score-badge ${getScoreClass(item.score)}`}>
                                {item.score}
                            </div>
                        </div>
                        <p className="score-feedback">{item.feedback}</p>
                    </div>
                ))}
            </div>

            <div className="implementation-section">
                <h3>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'text-bottom' }}>
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zM4 6h12v10H4V6z" clipRule="evenodd" />
                    </svg>
                    Implementation Plan
                </h3>
                <div className="implementation-content">
                    <ReactMarkdown>{report.implementation_plan}</ReactMarkdown>
                </div>
            </div>
        </div>
    );
};

export default AnalysisReport;
