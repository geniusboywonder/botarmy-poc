import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div className="min-h-screen bg-red-50 dark:bg-red-900 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-lg w-full">
            <div className="flex items-center mb-4">
              <div className="bg-red-100 dark:bg-red-800 rounded-full p-3 mr-4">
                <svg className="w-6 h-6 text-red-600 dark:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Something went wrong
              </h2>
            </div>
            
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              The application encountered an unexpected error. This might be due to:
            </p>
            
            <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 mb-4 space-y-1">
              <li>Frontend-backend API mismatch</li>
              <li>Missing or malformed data from the server</li>
              <li>Network connectivity issues</li>
              <li>Browser compatibility problems</li>
            </ul>
            
            <div className="bg-gray-100 dark:bg-gray-700 rounded p-3 mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Quick Fixes:</h3>
              <ol className="list-decimal list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li>Refresh the page (Ctrl+F5 or Cmd+Shift+R)</li>
                <li>Check browser console for detailed errors</li>
                <li>Ensure the backend server is running</li>
                <li>Clear browser cache and cookies</li>
              </ol>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                Reload Page
              </button>
              <button
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                Try Again
              </button>
            </div>
            
            {/* Debug info for development */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300">
                  Debug Information (Development Only)
                </summary>
                <div className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono overflow-auto max-h-32">
                  <div className="text-red-600 dark:text-red-400 mb-2">
                    Error: {this.state.error.toString()}
                  </div>
                  {this.state.errorInfo.componentStack && (
                    <div className="text-gray-600 dark:text-gray-300">
                      Component Stack: {this.state.errorInfo.componentStack}
                    </div>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
