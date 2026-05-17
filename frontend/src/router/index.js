import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getRole } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/Layout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'departments',
        name: 'AdminDepartments',
        component: () => import('@/views/admin/Departments.vue'),
        meta: { title: '部门管理' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '员工管理' }
      },
      {
        path: 'courses',
        name: 'AdminCourses',
        component: () => import('@/views/admin/Courses.vue'),
        meta: { title: '课程管理' }
      },
      {
        path: 'course-categories',
        name: 'AdminCourseCategories',
        component: () => import('@/views/admin/CourseCategories.vue'),
        meta: { title: '课程分类' }
      },
      {
        path: 'exams',
        name: 'AdminExams',
        component: () => import('@/views/admin/Exams.vue'),
        meta: { title: '考试管理' }
      },
      {
        path: 'questions',
        name: 'AdminQuestions',
        component: () => import('@/views/admin/Questions.vue'),
        meta: { title: '题库管理' }
      },
      {
        path: 'tasks',
        name: 'AdminTasks',
        component: () => import('@/views/admin/Tasks.vue'),
        meta: { title: '培训任务' }
      },
      {
        path: 'learning-paths',
        name: 'AdminLearningPaths',
        component: () => import('@/views/admin/LearningPaths.vue'),
        meta: { title: '学习路径' }
      },
      {
        path: 'progress',
        name: 'AdminProgress',
        component: () => import('@/views/admin/ProgressDashboard.vue'),
        meta: { title: '学习进度' }
      },
      {
        path: 'certificates',
        name: 'AdminCertificates',
        component: () => import('@/views/admin/Certificates.vue'),
        meta: { title: '证书管理' }
      },
      {
        path: 'certificate-templates',
        name: 'AdminCertificateTemplates',
        component: () => import('@/views/admin/CertificateTemplates.vue'),
        meta: { title: '证书模板' }
      },
      // ===== Phase 1 New Routes =====
      {
        path: 'files',
        name: 'AdminFiles',
        component: () => import('@/views/admin/FileManager.vue'),
        meta: { title: '文件管理' }
      },
      {
        path: 'online-editor',
        name: 'AdminOnlineEditor',
        component: () => import('@/views/admin/OnlineEditor.vue'),
        meta: { title: '在线编辑' }
      },
      {
        path: 'fetch-url',
        name: 'AdminFetchUrl',
        component: () => import('@/views/admin/FetchUrl.vue'),
        meta: { title: '网址抓取' }
      },
      {
        path: 'system-settings',
        name: 'AdminSystemSettings',
        component: () => import('@/views/admin/SystemSettings.vue'),
        meta: { title: '系统设置' }
      },
      {
        path: 'enterprise',
        name: 'AdminEnterprise',
        component: () => import('@/views/admin/EnterpriseSettings.vue'),
        meta: { title: '企业平台' }
      },
      {
        path: 'feedback-manage',
        name: 'AdminFeedbackManage',
        component: () => import('@/views/admin/FeedbackManage.vue'),
        meta: { title: '反馈管理' }
      },
      {
        path: 'reports',
        name: 'AdminReports',
        component: () => import('@/views/admin/ReportExport.vue'),
        meta: { title: '报告导出' }
      },
      {
        path: 'knowledge-graph',
        name: 'AdminKnowledgeGraph',
        component: () => import('@/views/student/KnowledgeGraph.vue'),
        meta: { title: '知识图谱' }
      },
    ]
  },
  {
    path: '/student',
    component: () => import('@/views/student/Layout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    redirect: '/student/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'StudentDashboard',
        component: () => import('@/views/student/Dashboard.vue'),
        meta: { title: '我的学习' }
      },
      {
        path: 'courses',
        name: 'StudentCourses',
        component: () => import('@/views/student/Courses.vue'),
        meta: { title: '课程中心' }
      },
      {
        path: 'courses/:id',
        name: 'StudentCourseDetail',
        component: () => import('@/views/student/CourseDetail.vue'),
        meta: { title: '课程详情' }
      },
      {
        path: 'courses/:courseId/lessons/:lessonId',
        name: 'StudentLessonPlayer',
        component: () => import('@/views/student/LessonPlayer.vue'),
        meta: { title: '课时学习' }
      },
      {
        path: 'exams',
        name: 'StudentExams',
        component: () => import('@/views/student/Exams.vue'),
        meta: { title: '我的考试' }
      },
      {
        path: 'exams/:id',
        name: 'StudentExamTaking',
        component: () => import('@/views/student/ExamTaking.vue'),
        meta: { title: '考试作答' }
      },
      {
        path: 'certificates',
        name: 'StudentCertificates',
        component: () => import('@/views/student/Certificates.vue'),
        meta: { title: '我的证书' }
      },
      {
        path: 'tasks',
        name: 'StudentTasks',
        component: () => import('@/views/student/Tasks.vue'),
        meta: { title: '我的任务' }
      },
      {
        path: 'notifications',
        name: 'StudentNotifications',
        component: () => import('@/views/student/Notifications.vue'),
        meta: { title: '通知中心' }
      },
      {
        path: 'feedback',
        name: 'StudentFeedback',
        component: () => import('@/views/student/Feedback.vue'),
        meta: { title: '评价反馈' }
      },
      {
        path: 'bookmarks',
        name: 'StudentBookmarks',
        component: () => import('@/views/student/Bookmarks.vue'),
        meta: { title: '我的收藏' }
      },
      {
        path: 'knowledge-graph',
        name: 'StudentKnowledgeGraph',
        component: () => import('@/views/student/KnowledgeGraph.vue'),
        meta: { title: '知识图谱' }
      },
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = getToken()
  const role = getRole()

  // 已登录用户访问登录页 → 跳到对应首页
  if (to.path === '/login') {
    if (token && role) {
      next(role === 'admin' || role === 'teacher' ? '/admin/dashboard' : '/student/dashboard')
      return
    }
    next()
    return
  }

  // 未登录 → 跳到登录
  if (!token) {
    next('/login')
    return
  }

  // 角色校验：admin/teacher 不能进 /student，student 不能进 /admin
  if (to.path.startsWith('/admin') && role === 'student') {
    next('/student/dashboard')
    return
  }
  if (to.path.startsWith('/student') && (role === 'admin' || role === 'teacher')) {
    next('/admin/dashboard')
    return
  }

  next()
})

export default router
