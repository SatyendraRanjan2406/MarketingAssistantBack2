import React from 'react';
import AIChatBox from './components/AIChatBox';

function App() {
  // Get token from environment variable or authentication context
  const token = process.env.REACT_APP_AUTH_TOKEN || '';

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg h-96">
            <AIChatBox token={token} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

