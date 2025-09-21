import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define which routes require authentication
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/accounts(.*)',
  '/assets(.*)',
  '/performance(.*)',
  '/perfomance(.*)',
  '/settings(.*)',
  '/new(.*)'
])

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api(.*)',
  '/login',
  '/register',
  // New public routes
  '/docs(.*)',
  '/help(.*)',
  '/api-docs(.*)',
  '/contact(.*)',
  '/privacy(.*)',
  '/terms(.*)',
  '/pricing(.*)',
  '/security(.*)',
  '/status(.*)'
])

export default clerkMiddleware(async (auth, req) => {
  // Allow public routes
  if (isPublicRoute(req)) {
    return
  }

  // Protect all other routes
  if (isProtectedRoute(req)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
