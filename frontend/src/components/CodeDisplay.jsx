import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, ArrowLeft } from 'lucide-react';

function CodeDisplay({ code, onBack }) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy code:', error);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="flex items-center space-x-2 text-dark-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Summaries</span>
          </button>
          <h2 className="text-2xl font-bold text-white">Generated Test Code</h2>
        </div>
        
        <button
          onClick={copyToClipboard}
          className="flex items-center space-x-2 bg-dark-700 hover:bg-dark-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-green-400" />
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy to Clipboard</span>
            </>
          )}
        </button>
      </div>

      {/* Code Display */}
      <div className="bg-dark-800 rounded-lg border border-dark-600 overflow-hidden">
        <div className="bg-dark-700 px-4 py-3 border-b border-dark-600">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <span className="text-dark-300 text-sm font-medium ml-4">
              test-file.test.js
            </span>
          </div>
        </div>
        
        <div className="relative">
          <SyntaxHighlighter
            language="javascript"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              padding: '1.5rem',
              background: 'transparent',
              fontSize: '14px',
              lineHeight: '1.6'
            }}
            showLineNumbers={true}
            lineNumberStyle={{
              color: '#64748b',
              paddingRight: '1rem',
              minWidth: '3rem'
            }}
          >
            {code}
          </SyntaxHighlighter>
        </div>
      </div>

      {/* Footer Info */}
      <div className="text-center text-dark-400 text-sm">
        <p>Generated test code using Code Llama AI model</p>
        <p className="mt-1">Review and modify the code as needed before using in your project</p>
      </div>
    </div>
  );
}

export default CodeDisplay;
