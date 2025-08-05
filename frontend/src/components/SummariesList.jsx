import { Code2, Loader2 } from 'lucide-react';

function SummariesList({ summaries, activeSummary, onSummarySelect, onGenerateCode, loading }) {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white mb-6">Test Case Summaries</h2>
      
      <div className="grid gap-3">
        {summaries.map((summary, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
              activeSummary === summary
                ? 'bg-blue-900/30 border-blue-500 shadow-lg'
                : 'bg-dark-800 border-dark-600 hover:border-dark-500 hover:bg-dark-750'
            }`}
            onClick={() => onSummarySelect(summary)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <Code2 className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  <span className="text-xs font-medium text-blue-400">
                    Test Case #{index + 1}
                  </span>
                </div>
                <p className="text-dark-200 text-sm leading-relaxed">
                  {summary}
                </p>
              </div>
              
              {activeSummary === summary && (
                <div className="ml-4 flex-shrink-0">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {activeSummary && (
        <div className="mt-6 p-4 bg-dark-800 rounded-lg border border-dark-600">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-dark-300 mb-1">
                Selected Test Case
              </h3>
              <p className="text-white text-sm">
                {activeSummary}
              </p>
            </div>
            
            <button
              onClick={onGenerateCode}
              disabled={loading}
              className="ml-4 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center space-x-2 flex-shrink-0"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Code2 className="w-4 h-4" />
                  <span>Generate Code</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SummariesList;
