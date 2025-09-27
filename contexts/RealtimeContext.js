import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { createClient } from '@supabase/supabase-js'
import { useAuth } from './AuthContext'
import toast from 'react-hot-toast'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

let supabase = null
if (supabaseUrl && supabaseKey) {
  supabase = createClient(supabaseUrl, supabaseKey)
}

const RealtimeContext = createContext({})

export const useRealtime = () => {
  const context = useContext(RealtimeContext)
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider')
  }
  return context
}

export const RealtimeProvider = ({ children }) => {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isConnected, setIsConnected] = useState(false)
  const [liveAnalytics, setLiveAnalytics] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [onlineUsers, setOnlineUsers] = useState([])

  // Initialize realtime connection
  useEffect(() => {
    if (!user || !supabase) return

    let subscription = null
    let sessionInterval = null

    const initializeRealtime = async () => {
      try {
        // Subscribe to notifications only
        subscription = supabase
          .channel('notifications')
          .on('postgres_changes', 
            { 
              event: 'INSERT', 
              schema: 'public', 
              table: 'notifications',
              filter: `user_id=eq.${user.id}`
            }, 
            (payload) => {
              const newNotification = payload.new
              setNotifications(prev => [newNotification, ...prev])
              setUnreadCount(prev => prev + 1)
              
              // Show toast notification
              toast.success(newNotification.title, {
                duration: 5000,
                icon: '🔔'
              })
            }
          )
          .subscribe()

        // Track user session (simplified - no frequent updates)
        const trackSession = async () => {
          try {
            await supabase
              .from('user_sessions')
              .upsert({
                user_id: user.id,
                is_online: true,
                last_seen: new Date().toISOString(),
                user_agent: navigator.userAgent
              }, {
                onConflict: 'user_id'
              })
          } catch (error) {
            console.error('Error tracking session:', error)
          }
        }

        // Track session only once on connection
        await trackSession()
        
        // Update session every 5 minutes (much less frequent)
        sessionInterval = setInterval(trackSession, 300000)

        setIsConnected(true)
      } catch (error) {
        console.error('Realtime connection error:', error)
        setIsConnected(false)
      }
    }

    initializeRealtime()

    // Cleanup on unmount
    return () => {
      if (subscription) {
        supabase.removeChannel(subscription)
      }
      if (sessionInterval) {
        clearInterval(sessionInterval)
      }
      setIsConnected(false)
    }
  }, [user])

  // Load initial data
  useEffect(() => {
    if (!user || !supabase) return

    const loadInitialData = async () => {
      try {
        // Load notifications
        const { data: notificationsData } = await supabase
          .from('notifications')
          .select('*')
          .eq('user_id', user.id)
          .order('created_at', { ascending: false })
          .limit(20)

        if (notificationsData) {
          setNotifications(notificationsData)
          setUnreadCount(notificationsData.filter(n => !n.read).length)
        }

        // Load chat messages
        const { data: chatData } = await supabase
          .from('chat_messages')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(50)

        if (chatData) {
          setChatMessages(chatData.reverse())
        }

        // Load analytics
        const { data: analyticsData } = await supabase
          .from('realtime_analytics')
          .select('*')
          .eq('user_id', user.id)
          .order('timestamp', { ascending: false })
          .limit(1)

        if (analyticsData && analyticsData.length > 0) {
          setLiveAnalytics(analyticsData[0])
        }

      } catch (error) {
        console.error('Error loading initial data:', error)
      }
    }

    loadInitialData()
  }, [user])

  // Send chat message
  const sendChatMessage = useCallback(async (message) => {
    if (!user || !supabase) return

    try {
      const { error } = await supabase
        .from('chat_messages')
        .insert({
          user_id: user.id,
          sender_name: user.user_metadata?.full_name || user.email,
          message: message,
          message_type: 'text'
        })

      if (error) throw error
    } catch (error) {
      console.error('Error sending chat message:', error)
      toast.error('Failed to send message')
    }
  }, [user])

  // Mark notification as read
  const markNotificationAsRead = useCallback(async (notificationId) => {
    if (!supabase) return

    try {
      const { error } = await supabase
        .from('notifications')
        .update({ read: true })
        .eq('id', notificationId)

      if (error) throw error

      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }, [])

  const value = {
    notifications,
    unreadCount,
    isConnected,
    liveAnalytics,
    chatMessages,
    onlineUsers,
    sendChatMessage,
    markNotificationAsRead
  }

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  )
}