import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Bot, User, Minimize2, Maximize2, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

export default function ChatBot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: 1,
          type: 'bot',
          message: "Hello! I'm your EduSense AI assistant. I can help you with:\n\n• Study tips and strategies\n• Quiz preparation\n• Learning path guidance\n• Performance analysis\n• General questions about your studies\n\nHow can I assist you today?",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [isOpen, messages.length]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !user) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      message: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Simulate AI response
      const botResponse = await generateBotResponse(inputMessage);
      
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'bot',
          message: botResponse,
          timestamp: new Date().toISOString()
        }]);
        setIsTyping(false);
      }, 1000 + Math.random() * 2000); // Random delay 1-3 seconds

    } catch (error) {
      console.error('Error generating response:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        message: "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
        timestamp: new Date().toISOString()
      }]);
      setIsTyping(false);
    }
  };

  const generateBotResponse = async (userMessage) => {
    const message = userMessage.toLowerCase();
    
    // Study tips and strategies
    if (message.includes('study') || message.includes('learn') || message.includes('prepare')) {
      return "Here are some effective study strategies:\n\n📚 **Active Learning**: Try explaining concepts out loud or teaching someone else\n⏰ **Pomodoro Technique**: Study for 25 minutes, then take a 5-minute break\n🎯 **Spaced Repetition**: Review material at increasing intervals\n📝 **Practice Testing**: Take quizzes and practice problems regularly\n\nWould you like me to help you create a study schedule?";
    }
    
    // Quiz preparation
    if (message.includes('quiz') || message.includes('test') || message.includes('exam')) {
      return "Great! Here's how to prepare for your quiz:\n\n🔍 **Review Key Concepts**: Focus on main topics and important details\n📊 **Take Practice Quizzes**: Use the quiz feature to test your knowledge\n📖 **Study Materials**: Review your uploaded materials and notes\n⏰ **Time Management**: Allocate time for each topic based on difficulty\n\nI can help you generate a practice quiz on any topic. What subject would you like to focus on?";
    }
    
    // Performance analysis
    if (message.includes('performance') || message.includes('score') || message.includes('progress')) {
      return "Let me help you analyze your performance:\n\n📈 **Track Your Progress**: Monitor your quiz scores over time\n🎯 **Identify Weak Areas**: Focus on topics where you score lower\n📊 **Set Goals**: Aim for consistent improvement in each subject\n🔄 **Regular Practice**: Consistent practice leads to better performance\n\nWould you like me to suggest specific areas for improvement based on your recent performance?";
    }
    
    // Learning paths
    if (message.includes('path') || message.includes('plan') || message.includes('schedule')) {
      return "I can help you create a personalized learning path:\n\n🎯 **Set Clear Goals**: Define what you want to achieve\n📚 **Choose Subjects**: Select the topics you want to focus on\n⏰ **Allocate Time**: Plan your study sessions effectively\n📈 **Track Progress**: Monitor your improvement over time\n\nWhat subjects are you most interested in learning?";
    }
    
    // General help
    if (message.includes('help') || message.includes('what can you do')) {
      return "I'm here to help you with your learning journey! I can assist with:\n\n📚 **Study Strategies**: Tips for effective learning\n🎯 **Quiz Preparation**: Help you prepare for tests\n📊 **Performance Analysis**: Track your progress\n🗺️ **Learning Paths**: Create personalized study plans\n💡 **Study Tips**: General advice for better learning\n\nJust ask me anything about your studies!";
    }
    
    // Math and science help
    if (message.includes('math') || message.includes('mathematics') || message.includes('calculus')) {
      return "Mathematics can be challenging, but here are some tips:\n\n🔢 **Practice Regularly**: Math requires consistent practice\n📐 **Understand Concepts**: Don't just memorize formulas\n🧮 **Work Through Examples**: Solve problems step by step\n📊 **Use Visual Aids**: Graphs and diagrams help understanding\n\nWould you like me to suggest some practice problems or explain a specific concept?";
    }
    
    // Science help
    if (message.includes('science') || message.includes('physics') || message.includes('chemistry')) {
      return "Science subjects require both theory and practice:\n\n🧪 **Understand Principles**: Focus on fundamental concepts\n🔬 **Visual Learning**: Use diagrams and models\n📚 **Connect Ideas**: Link different concepts together\n🧮 **Practice Problems**: Work through numerical problems\n\nWhat specific science topic would you like help with?";
    }
    
    // Motivation and encouragement
    if (message.includes('motivation') || message.includes('encourage') || message.includes('difficult')) {
      return "Learning can be challenging, but you're doing great! Here's some motivation:\n\n🌟 **Every Expert Was Once a Beginner**: Don't be discouraged by initial difficulties\n🎯 **Small Steps Lead to Big Results**: Consistent effort pays off\n📈 **Progress Over Perfection**: Focus on improvement, not perfection\n💪 **You've Got This**: Believe in your ability to learn and grow\n\nRemember, every question you ask and every problem you solve makes you stronger!";
    }
    
    // Default response
    return "That's an interesting question! I'm here to help you with your studies. You can ask me about:\n\n• Study strategies and tips\n• Quiz preparation\n• Learning paths\n• Performance analysis\n• Specific subject help\n• Motivation and encouragement\n\nWhat would you like to know more about?";
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        message: "Hello! I'm your EduSense AI assistant. How can I help you today?",
        timestamp: new Date().toISOString()
      }
    ]);
  };

  if (!user) return null; // Only show chat if user is logged in

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-indigo-600 text-white p-4 rounded-full shadow-lg hover:bg-indigo-700 transition-colors flex items-center justify-center"
          aria-label="Open AI Chat Assistant"
        >
          <MessageSquare className="h-6 w-6" />
        </button>
      )}

      {isOpen && (
        <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 w-96 flex flex-col ${
          isMinimized ? 'h-16' : 'h-96'
        } transition-all duration-300`}>
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b bg-indigo-600 text-white rounded-t-lg">
            <div className="flex items-center">
              <Bot className="h-5 w-5 mr-2" />
              <h3 className="font-semibold text-lg">AI Study Assistant</h3>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="text-white hover:text-indigo-100"
                aria-label={isMinimized ? "Expand chat" : "Minimize chat"}
              >
                {isMinimized ? <Maximize2 className="h-5 w-5" /> : <Minimize2 className="h-5 w-5" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-indigo-100"
                aria-label="Close chat"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages */}
              <div className="flex-grow p-4 overflow-y-auto custom-scrollbar">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`mb-4 ${msg.type === 'user' ? 'text-right' : 'text-left'}`}
                  >
                    <div className={`inline-block max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.type === 'user'
                        ? 'bg-indigo-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                    }`}>
                      <div className="flex items-start">
                        {msg.type === 'bot' && (
                          <Bot className="h-4 w-4 mr-2 mt-1 flex-shrink-0" />
                        )}
                        {msg.type === 'user' && (
                          <User className="h-4 w-4 mr-2 mt-1 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm whitespace-pre-line">{msg.message}</p>
                          <span className="text-xs opacity-70 block mt-1">
                            {new Date(msg.timestamp).toLocaleTimeString([], { 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="text-left">
                    <div className="inline-block bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-lg">
                      <div className="flex items-center">
                        <Bot className="h-4 w-4 mr-2" />
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 border-t dark:border-gray-700">
                <div className="flex items-center mb-2">
                  <button
                    onClick={clearChat}
                    className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    Clear Chat
                  </button>
                </div>
                <form onSubmit={handleSendMessage} className="flex">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ask me anything about your studies..."
                    className="flex-grow border dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-l-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    disabled={isTyping}
                  />
                  <button
                    type="submit"
                    className="bg-indigo-600 text-white px-4 py-2 rounded-r-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
                    disabled={!inputMessage.trim() || isTyping}
                    aria-label="Send message"
                  >
                    <Send className="h-5 w-5" />
                  </button>
                </form>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
