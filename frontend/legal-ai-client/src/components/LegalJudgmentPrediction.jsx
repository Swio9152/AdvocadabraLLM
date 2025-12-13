import React, { useState, useRef } from 'react';
import { Scale, FileText, TrendingUp, AlertCircle, CheckCircle, Loader } from 'lucide-react';

const LegalJudgmentPrediction = () => {
  const [inputText, setInputText] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const textareaRef = useRef(null);

  // Sample legal texts for testing
  const sampleTexts = [
    {
      title: "Defendant Entitled to Judgment",
      text: "The court holds that the defendant is entitled to judgment as a matter of law. The plaintiff has failed to present sufficient evidence to support their claims."
    },
    {
      title: "Plaintiff Wins Case", 
      text: "After careful consideration of all evidence presented, the court finds in favor of the plaintiff. The defendant's actions constitute a clear breach of contract."
    },
    {
      title: "Motion to Dismiss",
      text: "The defendant's motion to dismiss is granted. The plaintiff has failed to state a claim upon which relief can be granted."
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) {
      setError('Please enter legal case text');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/ljp/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('advocadabra_token')}`,
        },
        body: JSON.stringify({
          case_text: inputText
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        // Transform backend response to match frontend expectations
        const transformedResult = {
          prediction: result.prediction,
          probability: result.probability,
          prob_without_neighbors: result.explanation?.prob_without_neighbors,
          neighbor_influence_delta: result.explanation?.neighbor_influence,
          evidence: result.explanation?.evidence || []
        };
        setPrediction(transformedResult);
      } else {
        setError(result.error || 'Unknown error occurred');
      }
    } catch (err) {
      console.error('Prediction error:', err);
      setError('Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleText = (text) => {
    setInputText(text);
    setError(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const clearInput = () => {
    setInputText('');
    setPrediction(null);
    setError(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const getPredictionColor = (prediction) => {
    switch (prediction?.toLowerCase()) {
      case 'plaintiff':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'defendant':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'dismissal':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPredictionIcon = (prediction) => {
    switch (prediction?.toLowerCase()) {
      case 'plaintiff':
        return <CheckCircle className="w-5 h-5" />;
      case 'defendant':
        return <Scale className="w-5 h-5" />;
      case 'dismissal':
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3">
          <Scale className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Legal Judgment Prediction</h1>
        </div>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Enter legal case text to predict the likely judgment outcome using AI-powered analysis
        </p>
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Case Text Input
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="caseText" className="block text-sm font-medium text-gray-700 mb-2">
                  Enter legal case text or ruling description:
                </label>
                <textarea
                  ref={textareaRef}
                  id="caseText"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Paste or type legal case text here... For example: 'The court holds that the defendant is entitled to judgment as a matter of law.'"
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y min-h-[200px]"
                />
                <div className="text-sm text-gray-500 mt-1">
                  {inputText.length} characters
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading || !inputText.trim()}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
                >
                  {loading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-4 h-4" />
                      Predict Judgment
                    </>
                  )}
                </button>
                
                <button
                  type="button"
                  onClick={clearInput}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
              </div>
            </form>
          </div>

          {/* Sample Texts */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Legal Texts</h3>
            <div className="space-y-3">
              {sampleTexts.map((sample, index) => (
                <button
                  key={index}
                  onClick={() => handleSampleText(sample.text)}
                  className="w-full text-left p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                >
                  <div className="font-medium text-gray-900">{sample.title}</div>
                  <div className="text-sm text-gray-600 mt-1 truncate">{sample.text}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {prediction ? (
            <>
              {/* Main Prediction */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Scale className="w-5 h-5 text-blue-600" />
                  Prediction Results
                </h2>
                
                <div className="space-y-4">
                  <div className={`p-4 rounded-lg border-2 ${getPredictionColor(prediction.prediction)}`}>
                    <div className="flex items-center gap-3 mb-2">
                      {getPredictionIcon(prediction.prediction)}
                      <span className="text-lg font-bold capitalize">
                        {prediction.prediction}
                      </span>
                    </div>
                    <div className="text-sm opacity-80">
                      Predicted Outcome
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">
                        {(prediction.probability * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Confidence</div>
                    </div>
                    
                    {prediction.neighbor_influence_delta !== undefined && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900">
                          {prediction.neighbor_influence_delta > 0 ? '+' : ''}
                          {(prediction.neighbor_influence_delta * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">Neighbor Influence</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Evidence/Similar Cases */}
              {prediction.evidence && prediction.evidence.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Similar Cases Evidence</h3>
                  <div className="space-y-3">
                    {prediction.evidence.map((evidence, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-gray-900">Case #{evidence.case_id}</span>
                          <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            {(evidence.similarity * 100).toFixed(1)}% similar
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">{evidence.snippet}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detailed Analysis */}
              {prediction.prob_without_neighbors !== undefined && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Analysis</h3>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="font-medium text-gray-700">With Similar Cases</div>
                        <div className="text-lg font-bold text-gray-900">
                          {(prediction.probability * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div>
                        <div className="font-medium text-gray-700">Without Similar Cases</div>
                        <div className="text-lg font-bold text-gray-900">
                          {(prediction.prob_without_neighbors * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <div className="text-sm text-blue-800">
                        <strong>Analysis:</strong> The influence of similar cases 
                        {prediction.neighbor_influence_delta > 0 ? ' increased' : ' decreased'} 
                        the confidence by {Math.abs(prediction.neighbor_influence_delta * 100).toFixed(1)} percentage points.
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            /* Placeholder */
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
              <Scale className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Prediction Yet</h3>
              <p className="text-gray-600">
                Enter legal case text and click "Predict Judgment" to see AI analysis results.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LegalJudgmentPrediction;