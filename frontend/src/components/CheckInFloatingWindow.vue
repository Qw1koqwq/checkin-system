<template>
  <Teleport to="body">
    <Transition name="float">
      <div
        v-if="checkinStore.showFloatingWindow && checkinStore.activeCheckInCode"
        class="floating-window"
        :class="{ 'minimized': isMinimized, [`status-${windowStatusColor}`]: true }"
      >
        <div class="window-header" @click="toggleMinimize">
          <div class="header-left">
            <el-icon><CircleCheck /></el-icon>
            <span>签到进行中</span>
          </div>
          <div class="header-actions">
            <el-icon class="action-icon" @click.stop="toggleMinimize">
              <component :is="isMinimized ? 'ArrowUp' : 'ArrowDown'" />
            </el-icon>
            <el-icon class="action-icon close-icon" @click.stop="handleClose">
              <Close />
            </el-icon>
          </div>
        </div>
        
        <div v-show="!isMinimized" class="window-content">
          <div class="activity-info">
            <h3>{{ checkinStore.activeCheckInCode.activityTitle }}</h3>
          </div>
          
          <div class="code-display" :class="`code-${windowStatusColor}`">
            <div class="code-number">{{ checkinStore.activeCheckInCode.code }}</div>
          </div>
          
          <div class="code-info">
            <div class="countdown-display">
              <div class="countdown-label">剩余时间</div>
              <div class="countdown-time">{{ remainingTime }}</div>
            </div>
            <div class="countdown">
              <el-progress
                :percentage="countdownPercentage"
                :color="progressColor"
                :show-text="false"
              />
            </div>
            <div class="info-item">
              <el-icon><Timer /></el-icon>
              <span>有效期至: {{ formatTime(checkinStore.activeCheckInCode.expiresAt) }}</span>
            </div>
          </div>
          
          <div class="actions">
            <el-button
              type="primary"
              size="small"
              @click="goToCheckInPage"
            >
              查看详情
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleEndCheckIn"
            >
              结束签到
            </el-button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, Timer, ArrowUp, ArrowDown, Close } from '@element-plus/icons-vue'
import { useCheckinStore } from '@/stores/checkin'
import { checkinApi } from '@/api/checkin'
import dayjs from 'dayjs'

const router = useRouter()
const checkinStore = useCheckinStore()
const isMinimized = ref(false)
const currentTime = ref(Date.now())

let countdownInterval: number | null = null

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

const formatTime = (time: string) => {
  // 后端返回的UTC时间字符串已经带'Z'后缀，浏览器会自动转换为本地时间
  return dayjs(time).format('HH:mm:ss')
}

const remainingTime = computed(() => {
  if (!checkinStore.activeCheckInCode) return '00:00'
  
  // 使用响应式的currentTime以触发更新
  const now = new Date(currentTime.value)
  // 后端返回的UTC时间字符串已经带'Z'后缀
  const expires = new Date(checkinStore.activeCheckInCode.expiresAt)
  const diff = expires.getTime() - now.getTime()
  
  if (diff <= 0) return '已过期'
  
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const countdownPercentage = computed(() => {
  if (!checkinStore.activeCheckInCode) return 0
  
  // 使用响应式的currentTime以触发更新
  const now = new Date(currentTime.value)
  // 后端返回的UTC时间字符串已经带'Z'后缀
  const started = new Date(checkinStore.activeCheckInCode.startedAt)
  const expires = new Date(checkinStore.activeCheckInCode.expiresAt)
  
  const total = expires.getTime() - started.getTime()
  const elapsed = now.getTime() - started.getTime()
  
  if (elapsed <= 0) return 100
  if (elapsed >= total) return 0
  
  return Math.max(0, Math.min(100, ((total - elapsed) / total) * 100))
})

const progressColor = computed(() => {
  if (!checkinStore.activeCheckInCode) return '#67c23a'
  
  // 计算剩余时间（毫秒）
  const now = new Date(currentTime.value)
  const expires = new Date(checkinStore.activeCheckInCode.expiresAt)
  const remaining = expires.getTime() - now.getTime()
  
  // 计算总时间（毫秒）
  const started = new Date(checkinStore.activeCheckInCode.startedAt)
  const total = expires.getTime() - started.getTime()
  
  // 剩余1分钟或以下：红色
  if (remaining <= 60000) return '#f56c6c'
  
  // 剩余时间 ≤ 1/3 总时间：黄色
  if (remaining <= total / 3) return '#e6a23c'
  
  // 剩余时间 > 1/3 总时间：绿色
  return '#67c23a'
})

// 窗口状态颜色
const windowStatusColor = computed(() => {
  const color = progressColor.value
  if (color === '#f56c6c') return 'danger'
  if (color === '#e6a23c') return 'warning'
  return 'success'
})

const goToCheckInPage = () => {
  if (checkinStore.activeCheckInCode) {
    router.push(`/organizer/activities/${checkinStore.activeCheckInCode.activityId}/checkin`)
  }
}

const handleClose = () => {
  checkinStore.toggleFloatingWindow()
}

const handleEndCheckIn = async () => {
  try {
    await ElMessageBox.confirm('确定要结束当前签到吗？结束后签到码将立即失效。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (!checkinStore.activeCheckInCode) return
    
    await checkinApi.endCheckIn(checkinStore.activeCheckInCode.activityId)
    checkinStore.clearCheckInCode()
    ElMessage.success('签到已结束')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '结束签到失败')
    }
  }
}

const startCountdown = () => {
  // 立即更新一次当前时间，确保首次显示正确
  currentTime.value = Date.now()
  
  // 首次检查，如果已经过期则静默清除，不显示警告
  if (checkinStore.isExpired) {
    checkinStore.clearCheckInCode()
    return
  }
  
  // 清除旧的定时器
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  
  countdownInterval = window.setInterval(() => {
    // 更新当前时间，触发computed属性重新计算
    currentTime.value = Date.now()
    
    // 检查是否过期（运行中过期才显示警告）
    if (checkinStore.isExpired) {
      ElMessage.warning('签到码已过期')
      checkinStore.clearCheckInCode()
      if (countdownInterval) {
        clearInterval(countdownInterval)
      }
    }
  }, 1000)
}

// 监听activeCheckInCode的变化，立即更新时间
watch(
  () => checkinStore.activeCheckInCode,
  (newCode) => {
    if (newCode) {
      // 当签到码更新时，立即更新当前时间并重启倒计时
      currentTime.value = Date.now()
      startCountdown()
    }
  },
  { immediate: true }
)

onMounted(() => {
  // 如果已经有活跃的签到码，启动倒计时
  if (checkinStore.activeCheckInCode) {
    startCountdown()
  }
})

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})
</script>

<style scoped>
.floating-window {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 320px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* 成功状态 - 绿色 */
.floating-window.status-success {
  background: rgba(220, 252, 231, 0.75);
  border: 1px solid rgba(134, 239, 172, 0.3);
}

.floating-window.status-success .window-header {
  background: rgba(34, 197, 94, 0.85);
  border-bottom: 1px solid rgba(134, 239, 172, 0.3);
}

/* 警告状态 - 黄色 */
.floating-window.status-warning {
  background: rgba(254, 243, 199, 0.75);
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.floating-window.status-warning .window-header {
  background: rgba(245, 158, 11, 0.85);
  border-bottom: 1px solid rgba(251, 191, 36, 0.3);
}

/* 危险状态 - 红色 */
.floating-window.status-danger {
  background: rgba(254, 226, 226, 0.75);
  border: 1px solid rgba(248, 113, 113, 0.3);
}

.floating-window.status-danger .window-header {
  background: rgba(239, 68, 68, 0.85);
  border-bottom: 1px solid rgba(248, 113, 113, 0.3);
}

.floating-window.minimized {
  width: 200px;
}

.window-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: white;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-icon {
  cursor: pointer;
  font-size: 18px;
  transition: transform 0.2s;
}

.action-icon:hover {
  transform: scale(1.2);
}

.close-icon:hover {
  color: #f56c6c;
}

.window-content {
  padding: 16px;
}

.activity-info h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  text-align: center;
}

.code-display {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

/* 成功状态 - 绿色签到码框 */
.code-display.code-success {
  background: rgba(22, 163, 74, 0.9);
  border: 1px solid rgba(134, 239, 172, 0.4);
  box-shadow: 0 4px 16px rgba(22, 163, 74, 0.2);
}

/* 警告状态 - 黄色签到码框 */
.code-display.code-warning {
  background: rgba(217, 119, 6, 0.9);
  border: 1px solid rgba(251, 191, 36, 0.4);
  box-shadow: 0 4px 16px rgba(217, 119, 6, 0.2);
}

/* 危险状态 - 红色签到码框 */
.code-display.code-danger {
  background: rgba(220, 38, 38, 0.9);
  border: 1px solid rgba(248, 113, 113, 0.4);
  box-shadow: 0 4px 16px rgba(220, 38, 38, 0.2);
}

.code-number {
  font-size: 48px;
  font-weight: bold;
  color: white;
  letter-spacing: 8px;
  font-family: 'Courier New', monospace;
}

.code-info {
  margin-bottom: 16px;
}

.countdown-display {
  text-align: center;
  margin-bottom: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf0 100%);
  border-radius: 8px;
}

.countdown-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.countdown-time {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 12px;
  justify-content: center;
  margin-top: 8px;
}

.countdown {
  margin-bottom: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.actions .el-button {
  flex: 1;
}

.float-enter-active,
.float-leave-active {
  transition: all 0.3s ease;
}

.float-enter-from,
.float-leave-to {
  transform: translateY(100px);
  opacity: 0;
}
</style>
