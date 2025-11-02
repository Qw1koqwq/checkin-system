<template>
  <div class="manage-activities-page">
    <app-header />
    
    <div class="manage-activities">
      <div class="header">
        <h1>活动管理</h1>
        <el-button type="success" @click="handleExport" :loading="exportLoading">
          <el-icon><Download /></el-icon>
          导出活动列表
        </el-button>
      </div>

      <!-- Filters -->
      <div class="filters">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索活动标题"
          clearable
          style="width: 300px; margin-right: 16px"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="filterCategory"
          placeholder="选择分类"
          clearable
          style="width: 150px; margin-right: 16px"
          @change="handleSearch"
        >
          <el-option label="学术" value="academic" />
          <el-option label="文化" value="cultural" />
          <el-option label="体育" value="sports" />
          <el-option label="志愿" value="volunteer" />
          <el-option label="其他" value="other" />
        </el-select>

        <el-select
          v-model="filterStatus"
          placeholder="选择状态"
          clearable
          style="width: 150px; margin-right: 16px"
          @change="handleSearch"
        >
          <el-option label="未开始" value="upcoming" />
          <el-option label="进行中" value="ongoing" />
          <el-option label="已结束" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>

        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <!-- Activities Table -->
      <el-table
        :data="activities"
        v-loading="loading"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="活动标题" min-width="200" />
        <el-table-column label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="organizerName" label="组织者" width="120" />
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.startTime) }}
          </template>
        </el-table-column>
        <el-table-column label="人数" width="120">
          <template #default="{ row }">
            {{ row.currentParticipants }} / {{ row.maxParticipants }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="viewActivity(row.id)"
            >
              查看
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
              :disabled="row.status === 'ongoing'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import { activityApi } from '@/api/activity'
import type { Activity } from '@/types'

const router = useRouter()

const activities = ref<Activity[]>([])
const loading = ref(false)
const exportLoading = ref(false)

const searchKeyword = ref('')
const filterCategory = ref('')
const filterStatus = ref('')

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

// Fetch activities
const fetchActivities = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.value.page,
      pageSize: pagination.value.pageSize
    }

    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (filterCategory.value) {
      params.category = filterCategory.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }

    const response = await activityApi.getActivities(params)
    const data = response.data.data
    activities.value = data.items
    pagination.value.total = data.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动列表失败')
  } finally {
    loading.value = false
  }
}

// Search
const handleSearch = () => {
  pagination.value.page = 1
  fetchActivities()
}

// Pagination
const handlePageChange = (page: number) => {
  pagination.value.page = page
  fetchActivities()
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  fetchActivities()
}

// View activity
const viewActivity = (id: number) => {
  router.push(`/activities/${id}`)
}

// Delete activity
const handleDelete = async (activity: Activity) => {
  if (activity.status === 'ongoing') {
    ElMessage.warning('进行中的活动不能删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除活动"${activity.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await activityApi.adminDeleteActivity(activity.id)
    ElMessage.success('删除成功')
    fetchActivities()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// Export activities
const handleExport = async () => {
  exportLoading.value = true
  try {
    const response = await activityApi.adminExportActivities()
    
    // Create download link
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Get filename from response headers or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = `activities_${new Date().getTime()}.xlsx`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename=(.+)/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    exportLoading.value = false
  }
}

// Helper functions
const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = {
    academic: '学术',
    cultural: '文化',
    sports: '体育',
    volunteer: '志愿',
    other: '其他'
  }
  return map[category] || category
}

const getCategoryType = (category: string) => {
  const map: Record<string, any> = {
    academic: 'primary',
    cultural: 'success',
    sports: 'warning',
    volunteer: 'danger',
    other: 'info'
  }
  return map[category] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    upcoming: '未开始',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    upcoming: 'info',
    ongoing: 'success',
    completed: 'warning',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchActivities()
})
</script>

<style scoped lang="scss">
.manage-activities-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.manage-activities {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h1 {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .filters {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .pagination {
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
