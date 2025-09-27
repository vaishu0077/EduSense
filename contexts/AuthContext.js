import { createContext, useContext, useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import { useRouter } from 'next/router'
import toast from 'react-hot-toast'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

let supabase = null

if (supabaseUrl && supabaseKey) {
  supabase = createClient(supabaseUrl, supabaseKey)
} else {
  console.warn('Supabase environment variables not found. Authentication will use demo mode.')
}

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Initialize user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('edusense_user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
        setLoading(false) // Set loading to false immediately if we have saved user
      } catch (error) {
        console.error('Error parsing saved user:', error)
        localStorage.removeItem('edusense_user')
        setLoading(false)
      }
    } else {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let isInitialLoad = true

    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const sessionUser = session?.user || null
        
        // Only update if we don't have a user from localStorage or if session user is different
        setUser(prevUser => {
          if (!prevUser && sessionUser) {
            return sessionUser
          } else if (prevUser && !sessionUser) {
            return null
          } else if (prevUser?.id !== sessionUser?.id) {
            return sessionUser
          }
          return prevUser
        })
        
        setLoading(false)
        isInitialLoad = false
      } catch (error) {
        console.error('Error getting initial session:', error)
        setLoading(false)
        isInitialLoad = false
      }
    }

    getInitialSession()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        const newUser = session?.user || null
        
        // Only update state if user actually changed
        setUser(prevUser => {
          if (prevUser?.id === newUser?.id) {
            return prevUser // No change, return same user object
          }
          return newUser
        })
        
        setLoading(false)

        // Persist user data to localStorage
        if (newUser) {
          localStorage.setItem('edusense_user', JSON.stringify(newUser))
        } else {
          localStorage.removeItem('edusense_user')
        }

        // Only show messages and redirects for actual auth events, not session refreshes
        if (event === 'SIGNED_IN' && !isInitialLoad) {
          toast.success('Welcome to EduSense!')
          // Only redirect if not already on dashboard
          if (router.pathname !== '/') {
            router.push('/')
          }
        } else if (event === 'SIGNED_OUT') {
          toast.success('Logged out successfully')
          // Only redirect if not already on auth page
          if (router.pathname !== '/auth') {
            router.push('/auth')
          }
        }
        
        isInitialLoad = false
      }
    )

    return () => subscription.unsubscribe()
  }, [router])

  const signUp = async (email, password, userData) => {
    try {
      setLoading(true)
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: userData
        }
      })

      if (error) throw error

      if (data.user && !data.user.email_confirmed_at) {
        toast.success('Please check your email to confirm your account')
      }

      return { data, error: null }
    } catch (error) {
      toast.error(error.message)
      return { data: null, error }
    } finally {
      setLoading(false)
    }
  }

  const signIn = async (email, password) => {
    try {
      setLoading(true)
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      toast.error(error.message)
      return { data: null, error }
    } finally {
      setLoading(false)
    }
  }

  const signInWithGoogle = async () => {
    try {
      setLoading(true)
      
      if (!supabase) {
        throw new Error('Supabase not configured. Please set up your environment variables.')
      }
      
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: 'https://edusense-brown.vercel.app/auth/callback'
        }
      })

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      toast.error(error.message)
      return { data: null, error }
    } finally {
      setLoading(false)
    }
  }


  const signOut = async () => {
    try {
      setLoading(true)
      const { error } = await supabase.auth.signOut()
      if (error) throw error
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  const resetPassword = async (email) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`
      })

      if (error) throw error

      toast.success('Password reset email sent!')
      return { error: null }
    } catch (error) {
      toast.error(error.message)
      return { error }
    }
  }

  const updateProfile = async (updates) => {
    try {
      const { data, error } = await supabase.auth.updateUser({
        data: updates
      })

      if (error) throw error

      toast.success('Profile updated successfully')
      return { data, error: null }
    } catch (error) {
      toast.error(error.message)
      return { data: null, error }
    }
  }

  const value = {
    user,
    loading,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
    resetPassword,
    updateProfile,
    supabase
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
