import { useState, useRef, useEffect, FormEvent } from 'react';
import { Send, User, Bot } from 'lucide-react';
import { getChatCompletion } from '../config/ai';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      const response = await getChatCompletion(updatedMessages);
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] max-w-2xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-green-600 text-white p-4">
        <h2 className="text-xl font-bold">AkiLimo Assistant</h2>
        <p className="text-sm opacity-80">Your farming and market intelligence partner</p>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center text-gray-500">
            <div>
              <p className="text-xl font-medium mb-2">👋 Jambo!</p>
              <p className="mb-1">I'm AkiLimo, your farmer assistant.</p>
              <p>Ask me about:</p>
              <ul className="list-disc list-inside text-sm mt-2">
                <li>Best crops for your area</li>
                <li>Current market prices</li>
                <li>Transportation advice</li>
                <li>Weather forecasts</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div 
              key={index} 
              className={`flex mb-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`flex items-start max-w-[80%] ${message.role === 'user' 
                  ? 'bg-green-600 text-white rounded-l-2xl rounded-tr-2xl' 
                  : 'bg-white text-gray-800 rounded-r-2xl rounded-tl-2xl shadow'} p-3`}
              >
                {message.role === 'assistant' && (
                  <div className="mr-2 bg-green-100 text-green-600 p-1 rounded-full">
                    <Bot size={16} />
                  </div>
                )}
                <p className="text-sm">{message.content}</p>
                {message.role === 'user' && (
                  <div className="ml-2 bg-white/20 p-1 rounded-full">
                    <User size={16} />
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white rounded-r-2xl rounded-tl-2xl shadow p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {/* Input */}
      <form onSubmit={handleSubmit} className="flex p-4 border-t bg-white">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything about farming, markets, or transport..."
          className="flex-1 p-3 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="bg-green-600 text-white p-3 rounded-r-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 flex items-center justify-center"
          disabled={isLoading}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
