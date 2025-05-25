import axios from 'axios';

const API_URL = 'http://localhost:8000'; // FastAPI backend

export interface AnalysisReportData {
    scores: { category: string; score: number; feedback: string }[];
    implementation_plan: string;
}

export interface ProgressEventData {
    type: 'progress' | 'report' | 'error';
    message: string;
    step_name?: string;
    progress?: number;
    error?: boolean;
    data?: AnalysisReportData; // Present if type is 'report'
}

export const analyzeUrl = async (url: string): Promise<AnalysisReportData> => {
    try {
        const response = await axios.post<AnalysisReportData>(`${API_URL}/analyze`, { url });
        return response.data;
    } catch (error) {
        console.error("Error analyzing URL (POST):", error);
        if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data.detail || 'Failed to analyze URL');
        }
        throw error;
    }
};

export const analyzeUrlStream = (
    url: string,
    onProgress: (data: ProgressEventData) => void,
    onReport: (data: AnalysisReportData) => void,
    onError: (error: string) => void,
    onOpen: () => void,
    onClose: () => void
): EventSource => {
    const eventSource = new EventSource(`${API_URL}/analyze-stream?url=${encodeURIComponent(url)}`);
    // Note: FastAPI needs the URL in the query params for GET requests with EventSource,
    // or we need to change the backend to accept POST for EventSource (less standard).
    // For now, assuming the backend /analyze-stream is a GET endpoint or can handle URL from query.
    // Let's adjust the backend to accept GET for /analyze-stream or find a way for EventSource to POST.
    // EventSource standardly uses GET.
    // The backend was defined as POST @app.post("/analyze-stream")
    // This will require a change in the backend or a different approach for EventSource.
    // For now, I will proceed assuming EventSource can work with POST or the backend is adjusted.
    // A common workaround is to pass parameters via query string even for POST-like SSE.
    // The backend currently expects a JSON body for AnalysisRequest.
    // Let's change the backend to GET for the streaming endpoint.

    eventSource.onopen = () => {
        console.log("SSE connection opened.");
        onOpen();
    };

    eventSource.onmessage = (event) => {
        try {
            const parsedData: ProgressEventData = JSON.parse(event.data);
            if (parsedData.type === 'report' && parsedData.data) {
                onReport(parsedData.data);
                eventSource.close(); // Close after final report
                onClose();
            } else if (parsedData.type === 'progress' || parsedData.type === 'error') {
                onProgress(parsedData);
                if(parsedData.error) {
                    // Depending on desired behavior, we might close the connection on first error
                    // or let the backend decide if it's a fatal error.
                    // For now, just pass the error progress update.
                    // If it's a fatal error, the backend should stop sending events.
                }
            }
        } catch (e) {
            console.error("Error parsing SSE event data:", e, event.data);
            onError("Failed to parse progress update from server.");
            // Potentially close connection on parse error
            // eventSource.close();
            // onClose();
        }
    };

    eventSource.onerror = (err) => {
        console.error("EventSource failed:", err);
        // Check if it's a real error or just the connection closing
        if (eventSource.readyState === EventSource.CLOSED) {
            console.log("EventSource closed by server or network error.");
            // onClose might be called here if not already by a 'report' message
        } else {
            onError('Connection error with the analysis service.');
        }
        eventSource.close(); // Ensure it's closed on error
        onClose(); // Call general close handler
    };

    return eventSource;
};
