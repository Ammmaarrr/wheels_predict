"""
Modern UI Component Example
===========================
Sample implementation of a modern car price prediction interface
"""

from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/modern-ui')
def modern_ui():
    """Render modern car price prediction interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PakWheels - Car Price Prediction</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <h1 class="text-2xl font-bold text-blue-600">PakWheels AI</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                        Get Started
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Hero Section -->
        <div class="text-center mb-12">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
                AI-Powered Car Price Prediction
            </h2>
            <p class="text-xl text-gray-600 max-w-3xl mx-auto">
                Get accurate car valuations using advanced machine learning 
                trained on Pakistani market data
            </p>
        </div>

        <!-- Price Prediction Form -->
        <div class="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h3 class="text-2xl font-semibold mb-6">Predict Your Car's Value</h3>
            
            <form class="grid md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Car Make
                    </label>
                    <select class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500">
                        <option>Select Make</option>
                        <option>Toyota</option>
                        <option>Honda</option>
                        <option>Suzuki</option>
                        <option>Hyundai</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Model
                    </label>
                    <select class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500">
                        <option>Select Model</option>
                        <option>Corolla</option>
                        <option>Civic</option>
                        <option>Alto</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Year
                    </label>
                    <input type="number" min="2000" max="2025" 
                           class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                           placeholder="2020">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Engine Capacity (CC)
                    </label>
                    <input type="number" 
                           class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                           placeholder="1300">
                </div>
                
                <div class="md:col-span-2">
                    <button type="button" onclick="predictPrice()"
                            class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 font-medium">
                        🤖 Predict Price with AI
                    </button>
                </div>
            </form>
            
            <!-- Results Display -->
            <div id="results" class="hidden mt-8 p-6 bg-green-50 rounded-lg">
                <h4 class="text-lg font-semibold text-green-800 mb-2">
                    Predicted Price Range
                </h4>
                <div class="text-3xl font-bold text-green-600 mb-2">
                    PKR 2,500,000 - 2,800,000
                </div>
                <p class="text-green-700">
                    Based on current market trends and similar vehicles
                </p>
            </div>
        </div>

        <!-- Feature Cards -->
        <div class="grid md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    🤖
                </div>
                <h3 class="text-xl font-semibold mb-2">AI-Powered</h3>
                <p class="text-gray-600">
                    Advanced machine learning algorithms trained on extensive Pakistani market data
                </p>
            </div>
            
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    📊
                </div>
                <h3 class="text-xl font-semibold mb-2">Market Insights</h3>
                <p class="text-gray-600">
                    Real-time market analysis and pricing trends for informed decisions
                </p>
            </div>
            
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                    🎯
                </div>
                <h3 class="text-xl font-semibold mb-2">Accurate Results</h3>
                <p class="text-gray-600">
                    Highly accurate predictions with confidence intervals and explanations
                </p>
            </div>
        </div>
    </div>

    <script>
        function predictPrice() {
            // Show loading state
            const button = event.target;
            button.innerHTML = '⏳ Analyzing...';
            button.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                document.getElementById('results').classList.remove('hidden');
                button.innerHTML = '🤖 Predict Price with AI';
                button.disabled = false;
            }, 2000);
        }
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    app.run(debug=True, port=5001)
