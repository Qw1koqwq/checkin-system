<template>
  <div class="activity-detail-view">
    <app-header />
    
    <div v-loading="loading" class="container">
      <el-button :icon="ArrowLeft" @click="router.back()" class="back-btn">
        返回
      </el-button>

      <el-card v-if="activity" class="detail-card">
        <div class="activity-header">
          <div class="header-left">
            <h1>{{ activity.title }}</h1>
            <div class="tags">
              <el-tag :type="categoryType">{{ categoryLabel }}</el-tag>
              <el-tag :type="statusType" effect="plain">{{ statusLabel }}</el-tag>
            </div>
          </div>
          <div class="header-right">
            <template v-if="!authStore.isLoggedIn">
              <el-button
                type="primary"
                size="large"
                :icon="Lock"
                @click="goToLogin"
              >
                登录后报名
              </el-button>
            </template>
            <template v-else-if="authStore.isStudent">
              <el-button
                v-if="canRegister"
                type="primary"
                size="large"
                :icon="Check"
                :loading="registering"
                @click="handleRegister"
              >
                立即报名
              </el-button>
              <el-button
                v-else-if="isRegistered"
                type="success"
                size="large"
                :icon="CircleCheck"
                disabled
              >
                已报名
              </el-button>
              <el-button
                v-else
                type="info"
                size="large"
                disabled
              >
                报名已满
              </el-button>
            </template>
          </div>
        </div>

        <el-divider />

        <div class="activity-content">
          <div class="content-main">
            <div v-if="displayImages.length > 0" class="section">
              <h3><el-icon><Picture /></el-icon> 活动图片</h3>
              <div class="images-gallery">
                <el-image
                  v-for="(imageUrl, index) in displayImages"
                  :key="imageUrl"
                  :src="imageUrl"
                  :preview-src-list="displayImages"
                  :initial-index="index"
                  fit="cover"
                  class="gallery-image"
                  :preview-teleported="true"
                  :z-index="9999"
                >
                  <template #error>
                    <div class="image-slot">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
              </div>
            </div>

            <div class="section">
              <h3><el-icon><Document /></el-icon> 活动描述</h3>
              <p class="description">{{ activity.description }}</p>
            </div>

            <div class="section">
              <h3><el-icon><InfoFilled /></el-icon> 活动信息</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="活动ID">
                  <el-tag type="primary" size="large">{{ activity.id }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="活动分类">
                  <el-tag :type="categoryType">{{ categoryLabel }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="活动时间" :span="2">
                  {{ formatTime(activity.startTime) }} - {{ formatTime(activity.endTime) }}
                </el-descriptions-item>
                <el-descriptions-item label="活动地点" :span="2">
                  {{ activity.location }}
                </el-descriptions-item>
                <el-descriptions-item label="组织者">
                  {{ activity.organizerName }}
                </el-descriptions-item>
                <el-descriptions-item label="报名截止">
                  {{ formatTime(activity.registrationDeadline) }}
                </el-descriptions-item>
                <el-descriptions-item label="参与人数">
                  {{ activity.currentParticipants }} / {{ activity.maxParticipants }}
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  {{ formatTime(activity.createdAt) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <div v-if="activity.tags && activity.tags.length > 0" class="section">
              <h3><el-icon><PriceTag /></el-icon> 标签</h3>
              <div class="tags-list">
                <el-tag v-for="tag in activity.tags" :key="tag" type="info">
                  {{ tag }}
                </el-tag>
              </div>
            </div>

            <div v-if="activity.subItems && activity.subItems.length > 0" class="section">
              <h3><el-icon><List /></el-icon> 活动项目</h3>
              <div class="tags-list">
                <el-tag v-for="item in activity.subItems" :key="item.name" type="success" size="large">
                  {{ item.name }} ({{ item.currentParticipants || 0 }}/{{ item.maxParticipants }})
                </el-tag>
              </div>
            </div>
          </div>

          <div class="content-sidebar">
            <el-card shadow="never">
              <template #header>
                <div class="card-header">
                  <el-icon><TrendCharts /></el-icon>
                  <span>报名进度</span>
                </div>
              </template>
              <div class="progress-info">
                <el-progress
                  type="circle"
                  :percentage="participantPercentage"
                  :status="participantPercentage >= 100 ? 'success' : undefined"
                />
                <div class="progress-text">
                  <p>已报名 {{ totalCurrentParticipants }} 人</p>
                  <p>剩余 {{ totalMaxParticipants - totalCurrentParticipants }} 个名额</p>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-card>

      <!-- Sub-item selection dialog -->
      <el-dialog
        v-model="showSubItemDialog"
        title="选择参赛项目"
        width="500px"
      >
        <div style="margin-bottom: 16px; color: #606266;">
          请选择您要报名的项目：
        </div>
        <el-radio-group v-model="selectedSubItem" style="width: 100%;">
          <el-radio
            v-for="item in activity?.subItems"
            :key="item.name"
            :label="item.name"
            :disabled="(item.currentParticipants || 0) >= item.maxParticipants"
            size="large"
            style="display: block; margin-bottom: 12px; padding: 12px; border: 1px solid #dcdfe6; border-radius: 4px;"
          >
            <span>{{ item.name }}</span>
            <span style="margin-left: 8px; color: #909399; font-size: 13px;">
              ({{ item.currentParticipants || 0 }}/{{ item.maxParticipants }})
            </span>
            <el-tag v-if="(item.currentParticipants || 0) >= item.maxParticipants" type="danger" size="small" style="margin-left: 8px;">已满</el-tag>
          </el-radio>
        </el-radio-group>
        <template #footer>
          <el-button @click="showSubItemDialog = false">取消</el-button>
          <el-button type="primary" :loading="registering" @click="handleSubItemConfirm">
            确认报名
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useActivityStore } from '@/stores/activity'
import { registrationApi } from '@/api/registration'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import dayjs from 'dayjs'
import {
  ArrowLeft,
  Check,
  CircleCheck,
  Document,
  InfoFilled,
  PriceTag,
  TrendCharts,
  List,
  Picture,
  Lock
} from '@element-plus/icons-vue'
import type { Activity } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const activityStore = useActivityStore()

const activity = ref<Activity | null>(null)
const loading = ref(false)
const registering = ref(false)
const isRegistered = ref(false)
const selectedSubItem = ref<string>('')
const showSubItemDialog = ref(false)

const activityId = computed(() => Number(route.params.id))

const categoryType = computed(() => {
  if (!activity.value) return 'default'
  const types: Record<string, any> = {
    academic: 'primary',
    cultural: 'success',
    sports: 'warning',
    volunteer: 'info',
    other: 'default'
  }
  return types[activity.value.category] || 'default'
})

const categoryLabel = computed(() => {
  if (!activity.value) return ''
  const labels: Record<string, string> = {
    academic: '学术',
    cultural: '文艺',
    sports: '体育',
    volunteer: '志愿',
    other: '其他'
  }
  return labels[activity.value.category] || '其他'
})

const statusType = computed(() => {
  if (!activity.value) return 'default'
  const types: Record<string, any> = {
    upcoming: 'info',
    ongoing: 'success',
    completed: 'default',
    cancelled: 'danger'
  }
  return types[activity.value.status] || 'default'
})

const statusLabel = computed(() => {
  if (!activity.value) return ''
  const labels: Record<string, string> = {
    upcoming: '未开始',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return labels[activity.value.status] || '未知'
})

const totalCurrentParticipants = computed(() => {
  if (!activity.value) return 0
  
  // 如果有子项目，计算所有子项目的总报名人数
  if (activity.value.subItems && activity.value.subItems.length > 0) {
    return activity.value.subItems.reduce((sum, item) => 
      sum + (item.currentParticipants || 0), 0
    )
  }
  
  return activity.value.currentParticipants
})

const totalMaxParticipants = computed(() => {
  if (!activity.value) return 0
  
  // 如果有子项目，计算所有子项目的总人数限制
  if (activity.value.subItems && activity.value.subItems.length > 0) {
    return activity.value.subItems.reduce((sum, item) => 
      sum + item.maxParticipants, 0
    )
  }
  
  return activity.value.maxParticipants
})

const participantPercentage = computed(() => {
  if (totalMaxParticipants.value === 0) return 0
  return Math.round((totalCurrentParticipants.value / totalMaxParticipants.value) * 100)
})

const displayImages = computed(() => {
  if (!activity.value || !activity.value.images || activity.value.images.length === 0) {
    return []
  }
  return activity.value.images.map(img => getImageUrl(img))
})

const canRegister = computed(() => {
  if (!activity.value || !authStore.isLoggedIn || !authStore.isStudent) {
    console.log('canRegister: 基本条件不满足', {
      hasActivity: !!activity.value,
      isLoggedIn: authStore.isLoggedIn,
      isStudent: authStore.isStudent
    })
    return false
  }
  
  // 检查是否已报名
  if (isRegistered.value) {
    console.log('canRegister: 已报名')
    return false
  }
  
  // 检查活动状态和报名截止时间
  const now = new Date()
  // 后端返回的是UTC时间，需要正确解析
  const deadlineStr = activity.value.registrationDeadline.endsWith('Z') || 
                      activity.value.registrationDeadline.includes('+') 
                      ? activity.value.registrationDeadline 
                      : activity.value.registrationDeadline + 'Z'
  const deadline = new Date(deadlineStr)
  
  console.log('canRegister: 状态检查', {
    status: activity.value.status,
    deadlineOriginal: activity.value.registrationDeadline,
    deadline: deadline.toISOString(),
    deadlineLocal: deadline.toLocaleString(),
    now: now.toISOString(),
    nowLocal: now.toLocaleString(),
    isDeadlinePassed: deadline <= now
  })
  
  if ((activity.value.status !== 'upcoming' && activity.value.status !== 'ongoing') ||
      deadline <= now) {
    console.log('canRegister: 状态或时间不符合', {
      statusOk: activity.value.status === 'upcoming' || activity.value.status === 'ongoing',
      deadlineOk: deadline > now
    })
    return false
  }
  
  // 如果有子项目，检查是否有任何子项目还有空位
  if (activity.value.subItems && activity.value.subItems.length > 0) {
    console.log('canRegister: 检查子项目', {
      subItems: activity.value.subItems,
      hasAvailable: activity.value.subItems.some(item => 
        (item.currentParticipants || 0) < item.maxParticipants
      )
    })
    return activity.value.subItems.some(item => 
      (item.currentParticipants || 0) < item.maxParticipants
    )
  }
  
  // 没有子项目，检查总人数
  console.log('canRegister: 检查总人数', {
    current: activity.value.currentParticipants,
    max: activity.value.maxParticipants
  })
  return activity.value.currentParticipants < activity.value.maxParticipants
})

const formatTime = (time: string) => {
  // 后端返回的UTC时间字符串已经带'Z'后缀，浏览器会自动转换为本地时间
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

// 缓存 base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const BASE_URL_WITHOUT_API = API_BASE_URL.replace('/api', '')

const getImageUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) {
    return url
  }
  // 如果 URL 以 /api 开头，说明是完整的 API 路径，需要去掉 /api 前缀
  if (url.startsWith('/api/')) {
    return BASE_URL_WITHOUT_API + url
  }
  // 否则直接拼接
  return API_BASE_URL + url
}

onMounted(async () => {
  await loadActivity()
  if (authStore.isLoggedIn && authStore.isStudent) {
    await checkRegistrationStatus()
  }
})

const loadActivity = async () => {
  loading.value = true
  const result = await activityStore.fetchActivityById(activityId.value)
  if (result.success && result.data) {
    activity.value = result.data
  }
  loading.value = false
}

const checkRegistrationStatus = async () => {
  try {
    const response = await registrationApi.checkRegistrationStatus(activityId.value)
    isRegistered.value = response.data.data.isRegistered
  } catch (error) {
    console.error('Check registration status error:', error)
  }
}

const handleRegister = async () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请登录账号后才能进行报名')
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }

  // 如果有细分项目，显示选择对话框
  if (activity.value?.subItems && activity.value.subItems.length > 0) {
    showSubItemDialog.value = true
    return
  }

  // 没有细分项目，直接报名
  await submitRegistration()
}

const submitRegistration = async (subItem?: string) => {
  registering.value = true
  try {
    await registrationApi.register(activityId.value, subItem)
    ElMessage.success('报名成功')
    isRegistered.value = true
    showSubItemDialog.value = false
    if (activity.value) {
      activity.value.currentParticipants++
    }
  } catch (error: any) {
    ElMessage.error(error.message || '报名失败')
  } finally {
    registering.value = false
  }
}

const handleSubItemConfirm = () => {
  if (!selectedSubItem.value) {
    ElMessage.warning('请选择一个项目')
    return
  }
  submitRegistration(selectedSubItem.value)
}

const goToLogin = () => {
  router.push({ name: 'Login', query: { redirect: route.fullPath } })
}
</script>

<style scoped>
.activity-detail-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.back-btn {
  margin-bottom: 16px;
}

.detail-card {
  margin-bottom: 24px;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left h1 {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.tags {
  display: flex;
  gap: 8px;
}

.activity-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
}

.section {
  margin-bottom: 32px;
}

.section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.description {
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.progress-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.progress-text {
  text-align: center;
}

.progress-text p {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.images-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.gallery-image {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}

.gallery-image:hover {
  transform: scale(1.05);
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

@media (max-width: 768px) {
  .activity-content {
    grid-template-columns: 1fr;
  }
  
  .content-sidebar {
    order: -1;
  }
}
</style>
