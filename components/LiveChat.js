import React, { useState, useEffect, useRef } from 'react'
import { 
  MessageCircle, 
  Send, 
  X, 
  Minimize2, 
  Maximize2, 
  Users,
  Bot,
  User
} from 'lucide-react'
import { useRealtime } from '../contexts/RealtimeContext'
import { useAuth } from '../contexts/AuthContext'

const LiveChat = () => {
  const { user } = useAuth()
  const { chatMessages, sendChatMessage, onlineUsers } = useRealtime()
  
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [typingUsers, setTypingUsers] = useState([])
  
  const messagesEndRef = useRef(null)
  const chatContainerRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatMessages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!message.trim() || !user) return

    const messageText = message.trim()
    setMessage('')
    
    // Show typing indicator
    setIsTyping(true)
    
    try {
      await sendChatMessage(messageText)
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsTyping(false)
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const isOwnMessage = (messageUserId) => {
    return messageUserId === user?.id
  }

  const getMessageIcon = (messageUserId, senderName) => {
    if (isOwnMessage(messageUserId)) {
      return <User className="h-4 w-4 text-blue-500" />
    }
    if (senderName?.toLowerCase().includes('support') || senderName?.toLowerCase().includes('admin')) {
      return <Bot className="h-4 w-4 text-green-500" />
    }
    return <User className="h-4 w-4 text-gray-500" />
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <MessageCircle className="h-6 w-6" />
          <span className="hidden sm:block">Live Chat</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className={`bg-white rounded-lg shadow-xl border border-gray-200 ${
          isMinimized ? 'w-80 h-12' : 'w-96 h-96'
        } transition-all duration-300`}>
          {/* Chat Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageCircle className="h-5 w-5" />
              <div>
                <h3 className="font-semibold">Live Support</h3>
                <div className="flex items-center space-x-2 text-sm text-blue-100">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>{onlineUsers.length} online</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="text-blue-100 hover:text-white transition-colors"
              >
                {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-blue-100 hover:text-white transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages */}
              <div 
                ref={chatContainerRef}
                className="flex-1 overflow-y-auto p-4 space-y-3 h-64"
              >
                {chatMessages.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>Start a conversation!</p>
                    <p className="text-sm">Our support team is here to help.</p>
                  </div>
                ) : (
                  chatMessages.map((msg, index) => (
                    <div
                      key={index}
                      className={`flex ${isOwnMessage(msg.user_id) ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex items-start space-x-2 max-w-xs ${
                        isOwnMessage(msg.user_id) ? 'flex-row-reverse space-x-reverse' : ''
                      }`}>
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                          isOwnMessage(msg.user_id) 
                            ? 'bg-blue-500 text-white' 
                            : 'bg-gray-200 text-gray-600'
                        }`}>
                          {getMessageIcon(msg.user_id, msg.sender_name)}
                        </div>
                        <div className={`flex flex-col ${
                          isOwnMessage(msg.user_id) ? 'items-end' : 'items-start'
                        }`}>
                          <div className={`px-3 py-2 rounded-lg ${
                            isOwnMessage(msg.user_id)
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}>
                            <p className="text-sm">{msg.message}</p>
                          </div>
                          <div className="flex items-center space-x-1 mt-1">
                            <span className="text-xs text-gray-500">
                              {msg.sender_name}
                            </span>
                            <span className="text-xs text-gray-400">
                              {formatTime(msg.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
                
                {/* Typing Indicator */}
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-gray-600" />
                      </div>
                      <div className="bg-gray-100 px-3 py-2 rounded-lg">
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

              {/* Message Input */}
              <div className="border-t border-gray-200 p-4">
                <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={!user}
                  />
                  <button
                    type="submit"
                    disabled={!message.trim() || !user}
                    className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </form>
                {!user && (
                  <p className="text-xs text-gray-500 mt-2">
                    Please log in to send messages
                  </p>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default LiveChat
