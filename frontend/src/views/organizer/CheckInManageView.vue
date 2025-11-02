<template>
  <div class="checkin-manage-view">
    <app-header />
    
    <div v-loading="loading" class="container">
      <el-button :icon="ArrowLeft" @click="router.back()" class="back-btn">
        返回
      </el-button>

      <el-card v-if="activity" class="activity-info">
        <h2>{{ activity.title }}</h2>
        <div class="meta">
          <el-tag :type="getStatusType(activity.status)">
            {{ getStatusLabel(activity.status) }}
          </el-tag>
          <span>
            <el-icon><Clock /></el-icon>
            {{ formatTime(activity.startTime) }} - {{ formatTime(activity.endTime) }}
          </span>
          <span>
            <el-icon><Location /></el-icon>
            {{ activity.location }}
          </span>
        </div>
      </el-card>

      <el-row :gutter="24" class="content-row">
        <!-- 左侧：签到码 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>签到码</span>
                <div class="header-actions">
                  <el-select
                    v-if="!checkInCode"
                    v-model="codeDuration"
                    placeholder="选择时长"
                    style="width: 120px; margin-right: 8px;"
                    size="small"
                  >
                    <el-option label="5分钟" :value="5" />
                    <el-option label="10分钟" :value="10" />
                    <el-option label="15分钟" :value="15" />
                    <el-option label="20分钟" :value="20" />
                    <el-option label="30分钟" :value="30" />
                  </el-select>
                  <el-button
                    v-if="!checkInCode"
                    type="primary"
                    :icon="Refresh"
                    @click="generateCode"
                    :loading="generating"
                  >
                    生成签到码
                  </el-button>
                  <template v-else>
                    <el-button
                      type="warning"
                      :icon="Refresh"
                      @click="generateCode"
                      :loading="generating"
                      size="small"
                    >
                      重新生成
                    </el-button>
                    <el-button
                      type="danger"
                      @click="handleEndCheckIn"
                      :loading="ending"
                      size="small"
                    >
                      结束签到
                    </el-button>
                  </template>
                </div>
              </div>
            </template>

            <div v-if="checkInCode" class="code-display">
              <div v-if="isExpired" class="code-expired">
                <div class="expired-icon">⏰</div>
                <div class="expired-text">签到码已过期</div>
                <div class="expired-hint">请重新生成签到码</div>
              </div>
              <template v-else>
                <div class="code-number">{{ checkInCode.code }}</div>
                <div class="code-info">
                  <el-icon><Timer /></el-icon>
                  <span>有效期至: {{ formatTime(checkInCode.expiresAt) }}</span>
                </div>
                <div class="countdown">
                  <el-progress
                    :percentage="timePercentage"
                    :color="progressColor"
                    :stroke-width="10"
                    :show-text="false"
                  />
                  <div class="time-left">剩余 {{ timeLeft }}</div>
                </div>
              </template>
            </div>
            <el-empty v-else description="点击按钮生成签到码" />
          </el-card>

          <!-- 签到统计 -->
          <el-card class="stats-card">
            <template #header>
              <span>签到统计</span>
            </template>
            <el-row :gutter="16">
              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-value">{{ stats.totalRegistrations }}</div>
                  <div class="stat-label">总报名</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-value success">{{ stats.checkedIn }}</div>
                  <div class="stat-label">已签到</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-value">{{ stats.checkInRate }}%</div>
                  <div class="stat-label">签到率</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>

        <!-- 右侧：实时签到列表 -->
        <el-col :span="12">
          <el-card class="checkin-list-card">
            <template #header>
              <div class="card-header">
                <span>实时签到列表</span>
                <el-switch
                  v-model="autoRefresh"
                  active-text="自动刷新"
                  @change="handleAutoRefreshChange"
                />
              </div>
            </template>

            <div class="checkin-list">
              <el-timeline v-if="checkIns.length > 0">
                <el-timeline-item
                  v-for="checkin in checkIns"
                  :key="checkin.id"
                  :timestamp="formatTime(checkin.checkedInAt)"
                  placement="top"
                  :color="getCheckInColor(checkin)"
                >
                  <el-card shadow="hover" class="checkin-item">
                    <div class="checkin-content">
                      <div class="user-info">
                        <el-avatar :size="40">
                          {{ checkin.userName?.charAt(0) }}
                        </el-avatar>
                        <div class="user-details">
                          <div class="user-name">{{ checkin.userName }}</div>
                          <div class="user-email">{{ checkin.userEmail }}</div>
                        </div>
                      </div>
                      <el-tag :type="getMethodType(checkin.method)">
                        {{ getMethodLabel(checkin.method) }}
                      </el-tag>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-else description="暂无签到记录" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { activityApi } from '@/api/activity'
import { checkinApi } from '@/api/checkin'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import { useCheckinStore } from '@/stores/checkin'
import dayjs from 'dayjs'
import {
  ArrowLeft,
  Clock,
  Location,
  Refresh,
  Timer
} from '@element-plus/icons-vue'
import type { Activity, CheckIn, CheckInCode } from '@/types'

const router = useRouter()
const route = useRoute()
const checkinStore = useCheckinStore()

const activityId = Number(route.params.id)
const loading = ref(false)
const generating = ref(false)
const ending = ref(false)
const autoRefresh = ref(true)
const codeDuration = ref(15)
const activity = ref<Activity | null>(null)
const checkInCode = ref<CheckInCode | null>(null)
const checkIns = ref<CheckIn[]>([])
const stats = reactive({
  totalRegistrations: 0,
  checkedIn: 0,
  checkInRate: 0
})

let refreshTimer: number | null = null
let countdownTimer: number | null = null
const currentTime = ref(Date.now())

// 监听 store 中的 activeCheckInCode 变化，同步到本地
watch(
  () => checkinStore.activeCheckInCode,
  (newCode) => {
    // 如果 store 中的签到码被清除，并且是当前活动的签到码，则清除本地显示
    if (!newCode || newCode.activityId !== activityId) {
      checkInCode.value = null
    }
  }
)

onMounted(async () => {
  await loadActivity()
  await loadCheckIns()
  await loadStats()
  
  // 检查是否有当前活动的活跃签到码
  if (checkinStore.activeCheckInCode && 
      checkinStore.activeCheckInCode.activityId === activityId) {
    // 恢复签到码显示
    checkInCode.value = {
      code: checkinStore.activeCheckInCode.code,
      expiresAt: checkinStore.activeCheckInCode.expiresAt,
      activityId: activityId,
      createdAt: checkinStore.activeCheckInCode.startedAt
    }
  }
  
  if (autoRefresh.value) {
    startAutoRefresh()
  }
  startCountdown()
})

onUnmounted(() => {
  stopAutoRefresh()
  stopCountdown()
})

const loadActivity = async () => {
  loading.value = true
  try {
    const response = await activityApi.getActivityById(activityId)
    activity.value = response.data.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载活动失败')
  } finally {
    loading.value = false
  }
}

const generateCode = async () => {
  generating.value = true
  try {
    const response = await checkinApi.generateCode(activityId, codeDuration.value)
    checkInCode.value = response.data.data
    
    // 保存到全局store，显示悬浮窗
    if (activity.value && checkInCode.value) {
      checkinStore.setActiveCheckInCode({
        activityId: activity.value.id,
        activityTitle: activity.value.title,
        code: checkInCode.value.code,
        expiresAt: checkInCode.value.expiresAt,
        startedAt: new Date().toISOString()
      })
    }
    
    ElMessage.success(`签到码生成成功（有效期${codeDuration.value}分钟）`)
  } catch (error: any) {
    ElMessage.error(error.message || '生成签到码失败')
  } finally {
    generating.value = false
  }
}

const handleEndCheckIn = async () => {
  try {
    await ElMessageBox.confirm('确定要结束当前签到吗？结束后签到码将立即失效。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    ending.value = true
    await checkinApi.endCheckIn(activityId)
    
    // 清除签到码显示
    checkInCode.value = null
    
    // 清除全局store，隐藏悬浮窗
    checkinStore.clearCheckInCode()
    
    ElMessage.success('签到已结束')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '结束签到失败')
    }
  } finally {
    ending.value = false
  }
}

const loadCheckIns = async () => {
  try {
    const response = await checkinApi.getActivityCheckIns(activityId)
    checkIns.value = response.data.data
  } catch (error: any) {
    console.error('加载签到列表失败:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await checkinApi.getCheckInStats(activityId)
    const data = response.data.data
    stats.totalRegistrations = data.total
    stats.checkedIn = data.checkedIn
    stats.checkInRate = data.rate
  } catch (error: any) {
    console.error('加载统计失败:', error)
  }
}

const startAutoRefresh = () => {
  refreshTimer = window.setInterval(() => {
    loadCheckIns()
    loadStats()
  }, 3000) // 每3秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const startCountdown = () => {
  // 立即更新一次当前时间
  currentTime.value = Date.now()
  
  countdownTimer = window.setInterval(() => {
    currentTime.value = Date.now()
    
    // 检查签到码是否过期，如果过期则清除store中的签到码
    if (checkInCode.value && isExpired.value && checkinStore.activeCheckInCode) {
      if (checkinStore.activeCheckInCode.activityId === activityId) {
        checkinStore.clearCheckInCode()
      }
    }
  }, 1000)
}

const stopCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

const handleAutoRefreshChange = (value: boolean) => {
  if (value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const isExpired = computed(() => {
  if (!checkInCode.value) return false
  // 使用响应式的currentTime以触发更新
  const now = new Date(currentTime.value)
  const expires = new Date(checkInCode.value.expiresAt)
  return expires < now
})

const timeLeft = computed(() => {
  if (!checkInCode.value) return '00:00'
  // 后端返回的UTC时间字符串已经带'Z'后缀
  const expires = new Date(checkInCode.value.expiresAt).getTime()
  const diff = expires - currentTime.value
  if (diff <= 0) return '00:00'
  
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const timePercentage = computed(() => {
  if (!checkInCode.value) return 0
  // 后端返回的UTC时间字符串已经带'Z'后缀
  const created = new Date(checkInCode.value.createdAt).getTime()
  const expires = new Date(checkInCode.value.expiresAt).getTime()
  const total = expires - created
  const remaining = expires - currentTime.value
  return Math.max(0, Math.min(100, (remaining / total) * 100))
})

const progressColor = computed(() => {
  if (!checkInCode.value) return '#67c23a'
  
  // 计算剩余时间（毫秒）
  const now = new Date(currentTime.value)
  const expires = new Date(checkInCode.value.expiresAt)
  const remaining = expires.getTime() - now.getTime()
  
  // 计算总时间（毫秒）
  const created = new Date(checkInCode.value.createdAt)
  const total = expires.getTime() - created.getTime()
  
  // 剩余1分钟或以下：红色
  if (remaining <= 60000) return '#f56c6c'
  
  // 剩余时间 ≤ 1/3 总时间：黄色
  if (remaining <= total / 3) return '#e6a23c'
  
  // 剩余时间 > 1/3 总时间：绿色
  return '#67c23a'
})

const formatTime = (time: string) => {
  // 后端返回的UTC时间字符串已经带'Z'后缀，浏览器会自动转换为本地时间
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    upcoming: 'warning',
    ongoing: 'success',
    completed: 'info',
    cancelled: 'danger'
  }
  return types[status] || 'default'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    upcoming: '未开始',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return labels[status] || '未知'
}

const getCheckInColor = (checkin: CheckIn) => {
  const now = Date.now()
  const checkedTime = new Date(checkin.checkedInAt).getTime()
  const diff = now - checkedTime
  if (diff < 10000) return '#67c23a' // 10秒内，绿色
  if (diff < 60000) return '#409eff' // 1分钟内，蓝色
  return '#909399' // 更早，灰色
}

const getMethodType = (method: string) => {
  return method === 'qrcode' ? 'success' : 'primary'
}

const getMethodLabel = (method: string) => {
  return method === 'qrcode' ? '二维码' : '签到码'
}
</script>

<style scoped>
.checkin-manage-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.back-btn {
  margin-bottom: 16px;
}

.activity-info {
  margin-bottom: 24px;
}

.activity-info h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #606266;
}

.content-row {
  margin-top: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-display {
  text-align: center;
  padding: 24px;
}

.code-number {
  font-size: 72px;
  font-weight: bold;
  color: #409eff;
  letter-spacing: 8px;
  margin-bottom: 16px;
  font-family: 'Courier New', monospace;
}

.code-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #909399;
  margin-bottom: 24px;
}

.countdown {
  margin-bottom: 16px;
}

.time-left {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #606266;
  margin-top: 12px;
}

.code-expired {
  padding: 40px 20px;
  text-align: center;
}

.expired-icon {
  font-size: 64px;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

.expired-text {
  font-size: 28px;
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 8px;
}

.expired-hint {
  font-size: 14px;
  color: #909399;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.stats-card {
  margin-top: 24px;
}

.stat-item {
  text-align: center;
  padding: 16px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-value.success {
  color: #67c23a;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.checkin-list-card {
  height: calc(100vh - 400px);
  min-height: 500px;
}

.checkin-list {
  max-height: calc(100vh - 500px);
  overflow-y: auto;
}

.checkin-item {
  margin-bottom: 8px;
}

.checkin-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  text-align: left;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.user-email {
  font-size: 14px;
  color: #909399;
}
</style>
