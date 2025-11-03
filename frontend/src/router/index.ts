import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Cover',
    component: () => import('@/views/CoverView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/admin/manage-organizers',
    name: 'ManageOrganizers',
    component: () => import('@/views/admin/ManageOrganizersView.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/manage-activities',
    name: 'ManageActivities',
    component: () => import('@/views/admin/ManageActivitiesView.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/activities',
    name: 'Activities',
    component: () => import('@/views/student/ActivityListView.vue')
  },
  {
    path: '/activities/:id',
    name: 'ActivityDetail',
    component: () => import('@/views/student/ActivityDetailView.vue')
  },
  {
    path: '/my-activities',
    name: 'MyActivities',
    component: () => import('@/views/student/MyActivitiesView.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/checkin',
    name: 'CheckIn',
    component: () => import('@/views/student/CheckInView.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/checkin-code',
    name: 'CheckInCode',
    component: () => import('@/views/student/CheckInCodeView.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/organizer',
    redirect: '/organizer/dashboard'
  },
  {
    path: '/organizer/dashboard',
    name: 'OrganizerDashboard',
    component: () => import('@/views/organizer/DashboardView.vue'),
    meta: { requiresAuth: true, role: 'organizer' }
  },
  {
    path: '/organizer/activities',
    name: 'OrganizerActivities',
    component: () => import('@/views/organizer/ManageActivitiesView.vue'),
    meta: { requiresAuth: true, role: 'organizer' }
  },
  {
    path: '/organizer/activities/create',
    name: 'CreateActivity',
    component: () => import('@/views/organizer/CreateActivityView.vue'),
    meta: { requiresAuth: true, role: 'organizer' }
  },
  {
    path: '/organizer/activities/:id/edit',
    name: 'EditActivity',
    component: () => import('@/views/organizer/EditActivityView.vue'),
    meta: { requiresAuth: true, role: 'organizer' }
  },
  {
    path: '/organizer/activities/:id/checkin',
    name: 'CheckInManagement',
    component: () => import('@/views/organizer/CheckInManageView.vue'),
    meta: { requiresAuth: true, role: 'organizer' }
  },
  {
    path: '/organizer/activities/:id/statistics',
    name: 'ActivityStatistics',
    component: () => import('@/views/organizer/StatisticsView.vue'),
    meta: { requiresAuth: true, role: 'organizer' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const requiredRole = to.meta.role as string | undefined

  // Initialize auth from localStorage
  if (!authStore.accountUser && localStorage.getItem('accountUser')) {
    authStore.initAuth()
  }

  // Redirect logged-in users from cover page to their default page
  if (to.name === 'Cover' && authStore.isLoggedIn) {
    if (authStore.isAdmin) {
      next({ name: 'ManageOrganizers' })
    } else if (authStore.isOrganizer) {
      next({ name: 'OrganizerDashboard' })
    } else {
      next({ name: 'Activities' })
    }
    return
  }

  // Check if route requires authentication
  if (requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route requires guest (not logged in)
  if (requiresGuest && authStore.isLoggedIn) {
    next({ name: 'Activities' })
    return
  }

  // Check role-based access
  if (requiredRole) {
    const userRole = authStore.accountUser?.role || authStore.user?.role
    if (userRole !== requiredRole) {
      next({ name: 'Activities' })
      return
    }
  }

  next()
})

export default router
