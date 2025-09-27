# EduSense Deployment Guide

## 🚀 Quick Start - Deploy to Vercel in 5 Minutes

### Prerequisites
- GitHub account
- Vercel account (free)
- Supabase account (free)
- Google AI Studio account (free)

### Step 1: Set up Supabase (2 minutes)

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Click "New Project"
   - Choose organization and enter project name: `edusense`
   - Set database password (save it!)
   - Choose region closest to you
   - Click "Create new project"

2. **Set up Database Schema**
   - Go to SQL Editor in your Supabase dashboard
   - Copy and paste the contents of `supabase-schema.sql`
   - Click "Run" to execute the schema

3. **Get Supabase Credentials**
   - Go to Settings → API
   - Copy your Project URL and anon public key
   - Save these for later

### Step 2: Get Gemini API Key (1 minute)

1. **Create Google AI Studio Account**
   - Go to [makersuite.google.com](https://makersuite.google.com)
   - Sign in with Google account
   - Click "Get API Key"
   - Create a new API key
   - Copy the API key (save it!)

### Step 3: Deploy to Vercel (2 minutes)

1. **Fork/Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd edusense
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect it's a Next.js project

3. **Set Environment Variables**
   In Vercel dashboard, go to your project → Settings → Environment Variables:
   
   ```
   NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   GEMINI_API_KEY=your-gemini-api-key
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be live at `https://your-project.vercel.app`

## 🎯 Testing Your Deployment

### 1. Test Authentication
- Visit your deployed URL
- Click "Get Started"
- Try signing up with email or Google
- Verify user appears in Supabase Auth

### 2. Test AI Features
- Sign in to your account
- Go to Quiz page
- Click "Take a Quiz"
- Verify AI-generated quiz appears
- Test TTS/STT features

### 3. Test Analytics
- Complete a quiz
- Go to Progress page
- Verify charts and analytics display
- Check that data is saved to Supabase

## 🔧 Development Setup

### Local Development

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Set up Environment Variables**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your actual values
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```

4. **Visit Local App**
   - Open [http://localhost:3000](http://localhost:3000)

## 📊 Database Management

### Viewing Data in Supabase

1. **Go to Table Editor**
   - In Supabase dashboard, click "Table Editor"
   - View your tables: students, quizzes, questions, performance, etc.

2. **Monitor Real-time Data**
   - As users interact with your app, data will appear in real-time
   - Check the performance table for quiz results
   - Monitor quiz_attempts for user activity

### Adding Sample Data

```sql
-- Add more sample quizzes
INSERT INTO public.quizzes (topic, title, description, difficulty_level) VALUES
('Mathematics', 'Advanced Calculus', 'Test your calculus knowledge', 'hard'),
('Science', 'Physics Fundamentals', 'Basic physics concepts', 'medium'),
('History', 'World War II', 'Major events and causes', 'medium');

-- Add more sample questions
INSERT INTO public.questions (quiz_id, question_text, question_type, options, correct_answer, explanation) VALUES
((SELECT id FROM public.quizzes WHERE title = 'Advanced Calculus' LIMIT 1), 
 'What is the derivative of x²?', 'multiple_choice', 
 '["x", "2x", "x²", "2x²"]', '2x', 
 'The derivative of x² is 2x using the power rule');
```

## 🎨 Customization

### Styling
- Edit `tailwind.config.js` for theme customization
- Modify `styles/globals.css` for global styles
- Update component styles in individual files

### AI Prompts
- Edit API functions in `/api/` folder
- Customize Gemini prompts for different content types
- Adjust AI model parameters

### Features
- Add new pages in `/pages/` folder
- Create new components in `/components/` folder
- Add new API endpoints in `/api/` folder

## 🚀 Production Optimizations

### Performance
- Enable Vercel Analytics
- Optimize images with Next.js Image component
- Use Vercel Edge Functions for faster API responses

### Security
- Set up proper CORS policies
- Implement rate limiting
- Add input validation and sanitization

### Monitoring
- Set up Vercel monitoring
- Add error tracking (Sentry)
- Monitor API usage and costs

## 🔍 Troubleshooting

### Common Issues

1. **Environment Variables Not Working**
   - Check variable names match exactly
   - Ensure no extra spaces or quotes
   - Redeploy after changing variables

2. **Supabase Connection Issues**
   - Verify URL and key are correct
   - Check RLS policies are set up
   - Ensure database schema is created

3. **Gemini API Errors**
   - Verify API key is valid
   - Check API quota and limits
   - Ensure proper request format

4. **Build Errors**
   - Check Node.js version (18+)
   - Clear node_modules and reinstall
   - Check for TypeScript errors

### Getting Help

1. **Check Logs**
   - Vercel Function logs
   - Supabase logs
   - Browser console errors

2. **Debug Mode**
   - Add console.log statements
   - Use browser dev tools
   - Check network requests

3. **Community Support**
   - Vercel Discord
   - Supabase Discord
   - GitHub Issues

## 📈 Scaling Considerations

### Free Tier Limits
- **Vercel**: 100GB bandwidth, 100 serverless functions
- **Supabase**: 500MB database, 50MB file storage
- **Gemini API**: 15 requests per minute (free tier)

### Upgrade Path
- **Vercel Pro**: $20/month for more bandwidth and functions
- **Supabase Pro**: $25/month for more storage and features
- **Gemini API**: Pay-per-use pricing for higher limits

### Performance Tips
- Cache API responses
- Optimize database queries
- Use CDN for static assets
- Implement proper error handling

## 🎉 Success Metrics

### Key Performance Indicators
- User signups and retention
- Quiz completion rates
- AI feature usage (TTS/STT)
- Performance improvement over time

### Analytics Setup
- Google Analytics for user behavior
- Vercel Analytics for performance
- Custom metrics in Supabase
- A/B testing for features

---

## 🏆 Hackathon Presentation Tips

### Demo Flow (5 minutes)
1. **Show the Problem** (30 seconds)
   - "Students struggle with personalized learning"
   - "One-size-fits-all doesn't work"

2. **Demo the Solution** (3 minutes)
   - Sign up with Google
   - Take an AI-generated quiz
   - Show TTS/STT accessibility
   - Display real-time analytics

3. **Highlight Innovation** (1 minute)
   - Gemini AI integration
   - Accessibility-first design
   - Real-time performance tracking

4. **Show Impact** (30 seconds)
   - Scalable to millions of students
   - Free and accessible
   - Ready for production

### Key Talking Points
- **AI-Powered**: Uses cutting-edge Gemini 2.0 Flash
- **Accessible**: TTS/STT for inclusive learning
- **Real-time**: Live analytics and progress tracking
- **Scalable**: Serverless architecture on Vercel
- **Free**: No infrastructure costs for hackathon

### Technical Highlights
- Next.js 14 with App Router
- Supabase for real-time database
- Vercel serverless functions
- Tailwind CSS for modern UI
- Recharts for data visualization

---

**Your EduSense app is now live and ready to impress judges! 🚀📚✨**
