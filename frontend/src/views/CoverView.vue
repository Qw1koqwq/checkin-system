<template>
  <div class="cover-container">
    <!-- Animated background shapes -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
    </div>

    <!-- Main content -->
    <div class="cover-content">
      <!-- Logo and title -->
      <div class="logo-section">
        <div class="logo-icon">
          <el-icon :size="80"><Calendar /></el-icon>
        </div>
        <h1 class="system-title">班级活动报名系统</h1>
        <div class="title-divider"></div>
      </div>

      <!-- Feature highlights -->
      <div class="features">
        <div class="feature-item">
          <el-icon :size="32"><DocumentChecked /></el-icon>
          <span>便捷报名</span>
        </div>
        <div class="feature-item">
          <el-icon :size="32"><Clock /></el-icon>
          <span>实时签到</span>
        </div>
        <div class="feature-item">
          <el-icon :size="32"><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="goToLogin" class="enter-btn">
          <el-icon class="btn-icon"><Right /></el-icon>
          进入系统
        </el-button>
        <el-button size="large" @click="goToActivities" class="browse-btn">
          <el-icon class="btn-icon"><View /></el-icon>
          浏览活动
        </el-button>
      </div>

      <!-- Footer info -->
      <div class="footer-info">
        <p>让班级活动管理更简单高效</p>
      </div>
    </div>

    <!-- Decorative elements -->
    <div class="decorative-circles">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Calendar, DocumentChecked, Clock, DataAnalysis, Right, View } from '@element-plus/icons-vue'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}

const goToActivities = () => {
  router.push('/activities')
}
</script>

<style scoped>
.cover-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, 
    #e0f7fa 0%, 
    #b2ebf2 25%, 
    #c8e6c9 50%, 
    #a5d6a7 75%, 
    #81c784 100%
  );
  position: relative;
  overflow: hidden;
}

/* Animated background shapes */
.bg-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  animation: float 20s infinite ease-in-out;
}

.shape-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #4dd0e1, #26c6da);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #66bb6a, #4caf50);
  top: 60%;
  right: 15%;
  animation-delay: 5s;
}

.shape-3 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #80deea, #4dd0e1);
  bottom: 15%;
  left: 20%;
  animation-delay: 10s;
}

.shape-4 {
  width: 180px;
  height: 180px;
  background: linear-gradient(135deg, #81c784, #66bb6a);
  top: 20%;
  right: 25%;
  animation-delay: 15s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  75% {
    transform: translate(20px, 30px) scale(1.05);
  }
}

/* Decorative circles */
.decorative-circles {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  animation: pulse 4s infinite ease-in-out;
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -80px;
  left: -80px;
  animation-delay: 1.5s;
}

.circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 3s;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

/* Main content */
.cover-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border-radius: 24px;
  border: 2px solid rgba(255, 255, 255, 0.6);
  box-shadow: 
    0 20px 60px rgba(0, 150, 136, 0.15),
    0 8px 24px rgba(0, 188, 212, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  max-width: 700px;
  width: 90%;
  animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Logo section */
.logo-section {
  margin-bottom: 48px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  background: linear-gradient(135deg, #4dd0e1 0%, #26c6da 50%, #66bb6a 100%);
  border-radius: 50%;
  margin-bottom: 24px;
  box-shadow: 
    0 10px 30px rgba(38, 198, 218, 0.3),
    0 0 0 8px rgba(77, 208, 225, 0.1),
    0 0 0 16px rgba(77, 208, 225, 0.05);
  animation: logoFloat 3s infinite ease-in-out;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.logo-icon :deep(.el-icon) {
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.system-title {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #00897b 0%, #00acc1 50%, #43a047 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: 2px;
  text-shadow: 0 2px 10px rgba(0, 137, 123, 0.1);
}

.title-divider {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #4dd0e1, #66bb6a);
  margin: 24px auto 0;
  border-radius: 2px;
}

/* Features */
.features {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-bottom: 48px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(77, 208, 225, 0.2);
  transition: all 0.3s ease;
  min-width: 120px;
}

.feature-item:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(77, 208, 225, 0.4);
  box-shadow: 0 8px 20px rgba(77, 208, 225, 0.2);
}

.feature-item :deep(.el-icon) {
  color: #00acc1;
}

.feature-item span {
  font-size: 16px;
  font-weight: 500;
  color: #37474f;
}

/* Action buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.enter-btn,
.browse-btn {
  min-width: 160px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 24px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.enter-btn {
  background: linear-gradient(135deg, #00acc1 0%, #00897b 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(0, 172, 193, 0.3);
}

.enter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 172, 193, 0.4);
  background: linear-gradient(135deg, #00bcd4 0%, #00897b 100%);
}

.browse-btn {
  background: white;
  border: 2px solid #00acc1;
  color: #00acc1;
}

.browse-btn:hover {
  transform: translateY(-2px);
  background: rgba(0, 172, 193, 0.05);
  border-color: #00897b;
  color: #00897b;
  box-shadow: 0 4px 15px rgba(0, 172, 193, 0.2);
}

.btn-icon {
  font-size: 18px;
}

/* Footer info */
.footer-info {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 172, 193, 0.15);
}

.footer-info p {
  font-size: 14px;
  color: #78909c;
  margin: 0;
  font-weight: 400;
}

/* Responsive design */
@media (max-width: 768px) {
  .cover-content {
    padding: 40px 24px;
  }

  .system-title {
    font-size: 36px;
  }

  .logo-icon {
    width: 100px;
    height: 100px;
  }

  .logo-icon :deep(.el-icon) {
    font-size: 60px;
  }

  .features {
    gap: 24px;
  }

  .feature-item {
    min-width: 100px;
    padding: 16px;
  }

  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .enter-btn,
  .browse-btn {
    width: 100%;
  }
}
</style>
