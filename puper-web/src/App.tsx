/* eslint-disable @typescript-eslint/no-unused-vars */


// Create a client with optimized settings

function App() {
  return (
    <div className="min-h-screen bg-red-500 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">🚽 Puper</h1>
        <p className="text-gray-700 mb-6">Testing Tailwind CSS</p>
        <div className="space-y-4">
          <button className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Blue Button (Standard)
          </button>
          <button className="w-full bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded">
            Primary Button (Custom)
          </button>
          <div className="p-4 bg-primary-50 rounded border border-primary-200">
            <p className="text-primary-800">Custom primary colors test</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;