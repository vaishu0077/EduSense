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

    const initializeRealtime = async () => {
      try {
        // Subscribe to notifications
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
          .on('postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'performance',
              filter: `user_id=eq.${user.id}`
            },
            (payload) => {
              // Real-time progress update
              const newPerformance = payload.new
              setLiveAnalytics(prev => ({
                ...prev,
                latestScore: newPerformance.score,
                latestTopic: newPerformance.topic,
                lastUpdated: new Date().toISOString()
              }))
              
              toast.success(`Great job! Scored ${newPerformance.score}% on ${newPerformance.topic}`, {
                duration: 3000,
                icon: '📈'
              })
            }
          )
          .on('postgres_changes',
            {
              event: 'INSERT',
              schema: 'public',
              table: 'chat_messages'
            },
            (payload) => {
              const newMessage = payload.new
              setChatMessages(prev => [...prev, newMessage])
              
              // Only show toast if message is not from current user
              if (newMessage.user_id !== user.id) {
                toast.success(`New message from ${newMessage.sender_name}`, {
                  duration: 3000,
                  icon: '💬'
                })
              }
            }
          )
          .subscribe((status) => {
            setIsConnected(status === 'SUBSCRIBED')
          })

        // Load initial data
        await loadInitialData()
        
      } catch (error) {
        console.error('Realtime initialization error:', error)
      }
    }

    initializeRealtime()

    return () => {
      if (subscription) {
        subscription.unsubscribe()
      }
    }
  }, [user])

  const loadInitialData = async () => {
    if (!user) return

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

      // Load recent chat messages
      const { data: chatData } = await supabase
        .from('chat_messages')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)

      if (chatData) {
        setChatMessages(chatData.reverse())
      }

      // Load online users
      const { data: onlineUsersData } = await supabase
        .from('user_sessions')
        .select('user_id, last_seen')
        .gte('last_seen', new Date(Date.now() - 5 * 60 * 1000).toISOString()) // Last 5 minutes

      if (onlineUsersData) {
        setOnlineUsers(onlineUsersData)
      }

    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  }

  const markNotificationAsRead = useCallback(async (notificationId) => {
    try {
      await supabase
        .from('notifications')
        .update({ read: true })
        .eq('id', notificationId)

      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }, [])

  const markAllNotificationsAsRead = useCallback(async () => {
    try {
      await supabase
        .from('notifications')
        .update({ read: true })
        .eq('user_id', user.id)
        .eq('read', false)

      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error('Error marking all notifications as read:', error)
    }
  }, [user])

  const sendChatMessage = useCallback(async (message, recipientId = null) => {
    try {
      const { data, error } = await supabase
        .from('chat_messages')
        .insert({
          user_id: user.id,
          sender_name: user.user_metadata?.full_name || user.email,
          message: message,
          recipient_id: recipientId,
          created_at: new Date().toISOString()
        })

      if (error) throw error
      return { success: true, data }
    } catch (error) {
      console.error('Error sending chat message:', error)
      toast.error('Failed to send message')
      return { success: false, error }
    }
  }, [user])

  const sendNotification = useCallback(async (title, message, type = 'info', targetUserId = null) => {
    try {
      const { data, error } = await supabase
        .from('notifications')
        .insert({
          user_id: targetUserId || user.id,
          title: title,
          message: message,
          type: type,
          read: false,
          created_at: new Date().toISOString()
        })

      if (error) throw error
      return { success: true, data }
    } catch (error) {
      console.error('Error sending notification:', error)
      return { success: false, error }
    }
  }, [user])

  const updateUserPresence = useCallback(async () => {
    if (!user) return

    try {
      await supabase
        .from('user_sessions')
        .upsert({
          user_id: user.id,
          last_seen: new Date().toISOString(),
          is_online: true
        })
    } catch (error) {
      console.error('Error updating user presence:', error)
    }
  }, [user])

  // Update user presence every 30 seconds
  useEffect(() => {
    if (!user) return

    updateUserPresence()
    const interval = setInterval(updateUserPresence, 30000)

    return () => clearInterval(interval)
  }, [user, updateUserPresence])

  const value = {
    notifications,
    unreadCount,
    isConnected,
    liveAnalytics,
    chatMessages,
    onlineUsers,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    sendChatMessage,
    sendNotification,
    updateUserPresence
  }

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  )
}
