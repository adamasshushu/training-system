<template>
  <div class="lesson-player">
    <PageHeader :title="courseName" subtitle="课程学习">
      <template #actions>
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon> 返回课程
        </el-button>
      </template>
    </PageHeader>

    <div class="player-layout">
      <!-- Left: Main Content Area -->
      <div class="player-main">
        <!-- ========== Video Type ========== -->
        <div v-if="lessonType === 'video'" class="video-section">
          <!-- Video Player Wrapper -->
          <div class="video-wrapper" ref="videoWrapperRef"
            @mousemove="onWrapperMouseMove"
            @mouseleave="onWrapperMouseLeave"
          >
            <video
              ref="videoRef"
              :src="videoUrl"
              class="video-player"
              preload="auto"
              @loadedmetadata="onVideoMetaLoaded"
              @timeupdate="onTimeUpdate"
              @ended="onVideoEnded"
              @error="onVideoError"
              @waiting="onBuffering"
              @canplay="onCanPlay"
              @ratechange="onRateChange"
              @contextmenu.prevent
            ></video>

            <!-- Buffering spinner -->
            <transition name="fade">
              <div v-if="isBuffering && videoUrl" class="video-buffering">
                <el-icon class="loading-spinner" :size="36"><Loading /></el-icon>
              </div>
            </transition>

            <!-- Placeholder when no video -->
            <div v-if="!videoUrl" class="video-placeholder">
              <el-icon :size="64" color="#a29bfe"><VideoCameraFilled /></el-icon>
              <p>暂无可播放视频</p>
            </div>

            <!-- Center big play button (shown when paused) -->
            <transition name="scale-fade">
              <div v-if="videoUrl && !isPlaying" class="center-play-btn" @click="togglePlay">
                <div class="center-play-circle">
                  <el-icon :size="36" color="#fff"><VideoPlay /></el-icon>
                </div>
              </div>
            </transition>

            <!-- Bottom Control Bar -->
            <transition name="slide-up">
              <div v-if="videoUrl" class="control-bar" :class="{ visible: controlsVisible }">
                <!-- Progress bar -->
                <div class="progress-container">
                  <div
                    class="progress-track"
                    ref="progressRef"
                    @click="seekVideo"
                    @mousedown="startDragging"
                  >
                    <div class="progress-buffered" :style="{ width: bufferedPercent + '%' }"></div>
                    <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
                    <div class="progress-thumb" :style="{ left: progressPercent + '%' }"></div>
                  </div>
                </div>

                <!-- Control buttons row -->
                <div class="controls-row">
                  <div class="controls-left">
                    <button class="ctrl-btn" @click="togglePlay" :title="isPlaying ? '暂停' : '播放'">
                      <el-icon :size="20"><VideoPause v-if="isPlaying" /><VideoPlay v-else /></el-icon>
                    </button>
                    <span class="time-display">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
                  </div>

                  <div class="controls-right">
                    <!-- Volume -->
                    <div class="volume-control"
                      @mouseenter="volumeHover = true"
                      @mouseleave="volumeHover = false"
                    >
                      <button class="ctrl-btn" @click="toggleMute" :title="isMuted ? '取消静音' : '静音'">
                        <svg v-if="isMuted || volume === 0" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="color:#ef4444">
                          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                          <line x1="2" y1="2" x2="22" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                        </svg>
                      </button>
                      <div class="volume-slider-wrap" v-show="volumeHover">
                        <div class="volume-slider" @click="onVolumeSliderClick">
                          <div class="volume-fill" :style="{ height: volume * 100 + '%' }"></div>
                          <div class="volume-thumb" :style="{ bottom: volume * 100 + '%' }"></div>
                        </div>
                      </div>
                    </div>

                    <!-- Speed -->
                    <div class="speed-control"
                      @mouseenter="speedMenuOpen = true"
                      @mouseleave="speedMenuOpen = false"
                    >
                      <button class="ctrl-btn speed-btn">{{ playbackRate }}x</button>
                      <transition name="fade">
                        <div v-if="speedMenuOpen" class="speed-menu">
                          <div
                            v-for="speed in speedOptions"
                            :key="speed"
                            class="speed-option"
                            :class="{ active: playbackRate === speed }"
                            @click="setSpeed(speed)"
                          >
                            <span>{{ speed }}x</span>
                            <el-icon v-if="playbackRate === speed" size="14" color="#6C5CE7"><Check /></el-icon>
                          </div>
                        </div>
                      </transition>
                    </div>

                    <!-- Fullscreen -->
                    <button class="ctrl-btn" @click="toggleFullscreen" :title="isFullscreen ? '退出全屏' : '全屏'">
                      <el-icon :size="18" v-if="!isFullscreen"><FullScreen /></el-icon>
                      <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                        <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- Lesson info below video -->
          <SectionCard class="lesson-meta-card">
            <div class="lesson-meta-row">
              <div class="lesson-meta-left">
                <h2 class="lesson-title">{{ lessonTitle }}</h2>
                <el-tag size="small" :type="lessonTypeTag(lessonType)" effect="plain">
                  {{ lessonTypeLabel }}
                </el-tag>
              </div>
              <div class="lesson-meta-actions">
                <el-button
                  type="primary"
                  size="large"
                  :loading="submitting"
                  :disabled="isCompleted"
                  @click="markComplete"
                >
                  <el-icon><Check /></el-icon>
                  {{ isCompleted ? '已完成' : '完成学习' }}
                </el-button>
              </div>
            </div>
          </SectionCard>
        </div>

        <!-- ========== Document Type ========== -->
        <div v-else-if="lessonType === 'document'" class="non-video-section">
          <SectionCard title="文档预览" icon="📄">
            <div v-if="isPdf" class="pdf-viewer">
              <iframe :src="`/api/uploads/${docPath}?inline=1`" class="pdf-frame" frameborder="0"></iframe>
            </div>
            <div v-else-if="officeViewerUrl" class="office-viewer">
              <iframe :src="officeViewerUrl" class="office-frame" frameborder="0" allowfullscreen></iframe>
            </div>
            <div v-else class="doc-placeholder">
              <el-icon :size="56" color="#10b981"><Document /></el-icon>
              <p>暂不支持在线预览此文档类型</p>
              <el-button type="primary" :icon="Download" @click="downloadDoc">下载文件查看</el-button>
            </div>
          </SectionCard>
          <div class="doc-info-bar" v-if="fileUrl">
            <el-icon><Link /></el-icon>
            <span class="doc-name">{{ fileUrl.split('/').pop() }}</span>
            <el-button text type="primary" :icon="Download" @click="downloadDoc">下载</el-button>
          </div>
          <div class="action-bar">
            <el-button type="primary" size="large" :loading="submitting" :disabled="isCompleted" @click="markComplete">
              <el-icon><Check /></el-icon>
              {{ isCompleted ? '已完成' : '完成学习' }}
            </el-button>
          </div>
        </div>

        <!-- ========== Text / Markdown Type ========== -->
        <div v-else-if="lessonType === 'text'" class="non-video-section">
          <SectionCard title="课程内容" icon="📖">
            <div class="text-body markdown-body" v-html="renderedMarkdown"></div>
          </SectionCard>
          <div class="action-bar">
            <el-button type="primary" size="large" :loading="submitting" :disabled="isCompleted" @click="markComplete">
              <el-icon><Check /></el-icon>
              {{ isCompleted ? '已完成' : '完成学习' }}
            </el-button>
          </div>
        </div>

        <!-- ========== Unknown Type ========== -->
        <div v-else class="non-video-section">
          <SectionCard title="课时内容">
            <div class="unknown-placeholder">
              <p>不支持的课时类型：{{ lessonType }}</p>
            </div>
          </SectionCard>
        </div>
      </div>

      <!-- Right: Playlist Sidebar -->
      <div class="player-sidebar">
        <SectionCard title="课时列表" icon="📚">
          <template #extra>
            <span class="lesson-count">{{ totalLessons }} 个课时</span>
          </template>
          <div class="lesson-list">
            <div
              v-for="(chapter, cIdx) in allChapters"
              :key="chapter['ID'] || cIdx"
              class="chapter-group"
            >
              <div class="chapter-title">
                第{{ cIdx + 1 }}章 {{ chapter['标题'] }}
              </div>
              <div
                v-for="(les, lIdx) in chapter['课时列表']"
                :key="les['ID'] || lIdx"
                class="lesson-item"
                :class="{
                  active: les['ID'] === currentLessonId,
                  completed: les['是否完成']
                }"
                @click="navigateToLesson(les['ID'])"
              >
                <div class="lesson-item-icon">
                  <el-icon v-if="les['是否完成']" color="#10b981" size="16"><SuccessFilled /></el-icon>
                  <el-icon v-else size="16" color="var(--text-tertiary)">
                    <VideoPlay v-if="les['课时类型'] === 'video'" />
                    <Document v-else-if="les['课时类型'] === 'document'" />
                    <Reading v-else />
                  </el-icon>
                </div>
                <div class="lesson-item-content">
                  <span class="lesson-item-title">{{ les['标题'] }}</span>
                  <span class="lesson-item-type">{{ les['课时类型'] === 'video' ? '视频' : les['课时类型'] === 'document' ? '文档' : '图文' }}</span>
                </div>
                <div v-if="les['ID'] === currentLessonId" class="lesson-item-indicator"></div>
              </div>
            </div>
            <div v-if="allChapters.length === 0" class="lesson-list-empty">
              <el-icon :size="32" color="var(--text-tertiary)"><Folder /></el-icon>
              <p>暂无课时列表</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
  ArrowLeft,
  VideoCameraFilled,
  Document,
  Check,
  SuccessFilled,
  VideoPlay,
  Reading,
  Lock,
  Unlock,
  Download,
  Link,
  VideoPause,
  Loading,
  FullScreen,
  Folder
} from '@element-plus/icons-vue'
import { getCourseDetail, updateProgress } from '@/api/courses'

const route = useRoute()
const router = useRouter()
const courseId = route.params.courseId
const currentLessonId = ref(Number(route.params.lessonId))

const courseName = ref('')
const allChapters = ref([])
const lessonTitle = ref('')
const lessonType = ref('')
const lessonContent = ref('')
const videoUrl = ref('')
const fileUrl = ref('')
const isCompleted = ref(false)
const submitting = ref(false)

// Video player state
const videoRef = ref(null)
const disableFastForward = ref(false)

// --- New video player control state ---
const videoWrapperRef = ref(null)
const progressRef = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const isMuted = ref(false)
const playbackRate = ref(1)
const controlsVisible = ref(true)
const isBuffering = ref(false)
const volumeHover = ref(false)
const speedMenuOpen = ref(false)
const isFullscreen = ref(false)
const isDragging = ref(false)
const buffered = ref(0)
const hideControlsTimer = ref(null)

const speedOptions = [0.5, 0.75, 1, 1.25, 1.5, 2]

const totalLessons = computed(() => {
  let count = 0
  for (const ch of allChapters.value) {
    count += (ch['课时列表'] || []).length
  }
  return count
})

const progressPercent = computed(() => {
  if (!duration.value) return 0
  return (currentTime.value / duration.value) * 100
})

const bufferedPercent = computed(() => {
  if (!duration.value) return 0
  return (buffered.value / duration.value) * 100
})

const lessonTypeLabel = computed(() => {
  const map = { video: '视频', document: '文档', text: '图文' }
  return map[lessonType.value] || lessonType.value
})

const lessonTypeTag = (type) => {
  const map = { video: 'primary', document: 'success', text: 'warning' }
  return map[type] || 'info'
}

// Markdown rendering
const renderedMarkdown = computed(() => {
  if (!lessonContent.value) return '<p style="color:#94a3b8">暂无内容</p>'
  try {
    return DOMPurify.sanitize(marked.parse(lessonContent.value))
  } catch {
    return lessonContent.value
  }
})

// Document viewer
const isPdf = computed(() => {
  return fileUrl.value?.toLowerCase().endsWith('.pdf')
})

const docPath = computed(() => {
  if (!fileUrl.value) return ''
  const path = fileUrl.value.replace(/^\/api\/uploads\//, '')
  return path
})

const officeViewerUrl = computed(() => {
  if (!fileUrl.value || isPdf.value) return ''
  const ext = fileUrl.value.toLowerCase().split('.').pop()
  const officeExts = ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']
  if (!officeExts.includes(ext)) return ''
  const fileUrl_full = `${window.location.origin}/api/uploads/${docPath.value}`
  return `https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(fileUrl_full)}`
})

const downloadDoc = () => {
  if (fileUrl.value) {
    window.open(fileUrl.value.startsWith('http') ? fileUrl.value : `/api/uploads/${docPath.value}`, '_blank')
  }
}

const findLesson = () => {
  for (const ch of allChapters.value) {
    const lessons = ch['课时列表'] || []
    for (const les of lessons) {
      if (les['ID'] === currentLessonId.value) {
        return les
      }
    }
  }
  return null
}

const loadLesson = () => {
  const lesson = findLesson()
  if (lesson) {
    lessonTitle.value = lesson['标题'] || ''
    lessonType.value = lesson['课时类型'] || ''
    lessonContent.value = lesson['内容'] || ''
    videoUrl.value = lesson['视频地址'] || ''
    fileUrl.value = lesson['文件地址'] || lesson['file_url'] || ''
    isCompleted.value = !!lesson['是否完成']
    // Reset video player state when lesson changes
    resetPlayer()
  } else {
    lessonTitle.value = '课时未找到'
    lessonType.value = ''
  }
}

const navigateToLesson = (lessonId) => {
  currentLessonId.value = lessonId
  router.push(`/student/courses/${courseId}/lessons/${lessonId}`)
  loadLesson()
}

const goBack = () => {
  router.push(`/student/courses/${courseId}`)
}

const markComplete = async () => {
  submitting.value = true
  try {
    await updateProgress(courseId, {
      '课时ID': currentLessonId.value,
      '进度': 100,
      '是否完成': true
    })
    ElMessage.success('学习进度已保存')
    isCompleted.value = true
    for (const ch of allChapters.value) {
      const lessons = ch['课时列表'] || []
      for (const les of lessons) {
        if (les['ID'] === currentLessonId.value) {
          les['是否完成'] = true
        }
      }
    }
  } catch {
    ElMessage.error('保存进度失败')
  } finally {
    submitting.value = false
  }
}

const fetchData = async () => {
  try {
    const res = await getCourseDetail(courseId)
    courseName.value = res['数据']['标题'] || ''
    allChapters.value = res['数据']['章节列表'] || []
    loadLesson()
  } catch {
    ElMessage.error('加载课程信息失败')
  }
}

// --- Original video player methods ---
const onRateChange = () => {
  if (disableFastForward.value && videoRef.value) {
    if (videoRef.value.playbackRate > 1) {
      videoRef.value.playbackRate = 1
    }
  }
}

const onVideoLoaded = () => {
  if (disableFastForward.value && videoRef.value) {
    videoRef.value.playbackRate = 1
  }
}

const onVideoError = () => {
  console.warn('视频加载失败:', videoUrl.value)
}

const onToggleChange = (val) => {
  if (val && videoRef.value) {
    videoRef.value.playbackRate = 1
  }
}

const handleKeyDown = (e) => {
  if (!disableFastForward.value) return
  if (e.key === '>' || e.key === '.' || e.key === '<' || e.key === ',') {
    e.preventDefault()
  }
}

// --- New video player control methods ---

const resetPlayer = () => {
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
  buffered.value = 0
  isBuffering.value = false
  playbackRate.value = 1
  controlsVisible.value = true
}

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  const pad = (n) => n.toString().padStart(2, '0')
  if (h > 0) return `${h}:${pad(m)}:${pad(s)}`
  return `${m}:${pad(s)}`
}

const togglePlay = () => {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play().catch(() => {})
    isPlaying.value = true
  } else {
    videoRef.value.pause()
    isPlaying.value = false
  }
}

const toggleMute = () => {
  if (!videoRef.value) return
  videoRef.value.muted = !videoRef.value.muted
  isMuted.value = videoRef.value.muted
}

const onVolumeSliderClick = (e) => {
  if (!videoRef.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const y = rect.bottom - e.clientY
  const h = rect.height
  const val = Math.max(0, Math.min(1, y / h))
  volume.value = val
  videoRef.value.volume = val
  if (val > 0 && videoRef.value.muted) {
    videoRef.value.muted = false
    isMuted.value = false
  }
}

const seekVideo = (e) => {
  if (!videoRef.value || !duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const percent = x / rect.width
  const time = percent * duration.value
  videoRef.value.currentTime = time
  currentTime.value = time
}

const startDragging = (e) => {
  isDragging.value = true
  document.addEventListener('mousemove', onDragging)
  document.addEventListener('mouseup', stopDragging)
}

const onDragging = (e) => {
  if (!videoRef.value || !duration.value || !progressRef.value) return
  const rect = progressRef.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width))
  const percent = x / rect.width
  const time = percent * duration.value
  currentTime.value = time
  videoRef.value.currentTime = time
}

const stopDragging = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDragging)
  document.removeEventListener('mouseup', stopDragging)
}

const setSpeed = (speed) => {
  if (!videoRef.value) return
  videoRef.value.playbackRate = speed
  playbackRate.value = speed
  speedMenuOpen.value = false
}

const toggleFullscreen = async () => {
  if (!videoWrapperRef.value) return
  if (!document.fullscreenElement) {
    try {
      await videoWrapperRef.value.requestFullscreen()
      isFullscreen.value = true
    } catch { /* ignore */ }
  } else {
    try {
      await document.exitFullscreen()
      isFullscreen.value = false
    } catch { /* ignore */ }
  }
}

const onVideoMetaLoaded = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration
    volume.value = videoRef.value.volume
  }
  // Call original handler
  onVideoLoaded()
}

const onTimeUpdate = () => {
  if (videoRef.value && !isDragging.value) {
    currentTime.value = videoRef.value.currentTime
  }
}

const onVideoEnded = () => {
  isPlaying.value = false
}

const onBuffering = () => {
  isBuffering.value = true
}

const onCanPlay = () => {
  isBuffering.value = false
  if (videoRef.value) {
    try {
      buffered.value = videoRef.value.buffered.length > 0
        ? videoRef.value.buffered.end(videoRef.value.buffered.length - 1)
        : 0
    } catch { /* ignore */ }
  }
}

const showControls = () => {
  controlsVisible.value = true
  clearTimeout(hideControlsTimer.value)
}

const hideControls = () => {
  if (isPlaying.value) {
    hideControlsTimer.value = setTimeout(() => {
      controlsVisible.value = false
    }, 3000)
  }
}

const onWrapperMouseMove = () => {
  controlsVisible.value = true
  clearTimeout(hideControlsTimer.value)
  if (isPlaying.value) {
    hideControlsTimer.value = setTimeout(() => {
      controlsVisible.value = false
    }, 3000)
  }
}

const onWrapperMouseLeave = () => {
  if (isPlaying.value) {
    hideControlsTimer.value = setTimeout(() => {
      controlsVisible.value = false
    }, 2000)
  }
}

// Keyboard shortcuts
const onKeyDown = (e) => {
  // Only handle when video is active
  if (lessonType.value !== 'video') return

  switch (e.code) {
    case 'Space':
      e.preventDefault()
      togglePlay()
      break
    case 'KeyF':
      e.preventDefault()
      toggleFullscreen()
      break
    case 'ArrowLeft':
      if (videoRef.value) {
        videoRef.value.currentTime = Math.max(0, videoRef.value.currentTime - 5)
      }
      break
    case 'ArrowRight':
      if (videoRef.value) {
        videoRef.value.currentTime = Math.min(duration.value, videoRef.value.currentTime + 5)
      }
      break
    case 'ArrowUp':
      e.preventDefault()
      if (videoRef.value) {
        volume.value = Math.min(1, volume.value + 0.1)
        videoRef.value.volume = volume.value
      }
      break
    case 'ArrowDown':
      e.preventDefault()
      if (videoRef.value) {
        volume.value = Math.max(0, volume.value - 0.1)
        videoRef.value.volume = volume.value
      }
      break
    case 'KeyM':
      toggleMute()
      break
  }
}

// Fullscreen change listener
const onFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

onMounted(() => {
  fetchData()
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keydown', onKeyDown)
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keydown', onKeyDown)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  clearTimeout(hideControlsTimer.value)
})
</script>

<style scoped>
/* ===== Layout ===== */
.lesson-player {
  max-width: 1240px;
  margin: 0 auto;
  padding: 20px 24px 40px;
}

.player-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.player-main {
  flex: 1;
  min-width: 0;
}

.player-sidebar {
  width: 300px;
  flex-shrink: 0;
  position: sticky;
  top: 20px;
}

/* ===== Video Player ===== */
.video-section {
  margin-bottom: 0;
}

.video-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #0f0f1a;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--border-default);
}

.video-player {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  background: #0f0f1a;
}

/* Placeholder */
.video-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-tertiary);
  background: #0f0f1a;
}
.video-placeholder p {
  font-size: 15px;
  margin: 0;
}

/* Buffering */
.video-buffering {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 15, 26, 0.5);
  z-index: 5;
}
.loading-spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Center play button */
.center-play-btn {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 6;
  cursor: pointer;
}
.center-play-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(108, 92, 231, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, background 0.2s;
  backdrop-filter: blur(4px);
}
.center-play-circle:hover {
  transform: scale(1.08);
  background: rgba(108, 92, 231, 1);
}

/* Control bar */
.control-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.85));
  padding: 40px 16px 10px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.control-bar.visible {
  opacity: 1;
}

/* Progress bar */
.progress-container {
  padding: 4px 0;
  cursor: pointer;
  margin-bottom: 6px;
}
.progress-track {
  position: relative;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  cursor: pointer;
  transition: height 0.15s;
}
.progress-track:hover {
  height: 6px;
}
.progress-buffered {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  transition: width 0.2s;
}
.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #6C5CE7;
  border-radius: 2px;
  transition: width 0.1s linear;
}
.progress-thumb {
  position: absolute;
  top: 50%;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #6C5CE7;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.15s;
  pointer-events: none;
}
.progress-track:hover .progress-thumb {
  opacity: 1;
}

/* Controls row */
.controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.controls-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.controls-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Control buttons */
.ctrl-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 6px;
  transition: background 0.15s;
  font-size: 13px;
}
.ctrl-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.time-display {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  font-variant-numeric: tabular-nums;
  user-select: none;
}

.speed-btn {
  font-size: 13px;
  font-weight: 600;
  min-width: 36px;
  letter-spacing: 0.3px;
}

/* Volume control */
.volume-control {
  position: relative;
  display: flex;
  align-items: center;
}
.volume-slider-wrap {
  position: absolute;
  bottom: 36px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(30, 30, 50, 0.95);
  border-radius: 8px;
  padding: 8px 6px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.volume-slider {
  position: relative;
  width: 4px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  cursor: pointer;
}
.volume-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #6C5CE7;
  border-radius: 2px;
  transition: height 0.1s;
}
.volume-thumb {
  position: absolute;
  left: 50%;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  transform: translate(-50%, 50%);
  box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}

/* Speed selector */
.speed-control {
  position: relative;
  display: flex;
  align-items: center;
}
.speed-menu {
  position: absolute;
  bottom: 36px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(30, 30, 50, 0.95);
  border-radius: 10px;
  padding: 4px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  min-width: 72px;
  z-index: 20;
}
.speed-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 12px;
  cursor: pointer;
  border-radius: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.speed-option:hover {
  background: rgba(108, 92, 231, 0.2);
  color: #fff;
}
.speed-option.active {
  color: #6C5CE7;
  font-weight: 600;
}

/* ===== Lesson Meta Card ===== */
.lesson-meta-card {
  margin-top: 16px;
}
.lesson-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.lesson-meta-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}
.lesson-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.lesson-meta-actions {
  flex-shrink: 0;
}

/* ===== Sidebar / Playlist ===== */
.lesson-count {
  font-size: 12px;
  color: var(--text-tertiary);
}
.lesson-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding-right: 4px;
}
.lesson-list::-webkit-scrollbar {
  width: 4px;
}
.lesson-list::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: 2px;
}

.chapter-group {
  margin-bottom: 10px;
}
.chapter-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  padding: 6px 4px 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.15s, transform 0.1s;
  position: relative;
}
.lesson-item:hover {
  background: var(--bg-hover);
}
.lesson-item.active {
  background: rgba(108, 92, 231, 0.08);
  border-left: 3px solid #6C5CE7;
  padding-left: 7px;
}
.lesson-item.completed .lesson-item-title {
  color: #10b981;
}

.lesson-item-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  width: 20px;
  justify-content: center;
}

.lesson-item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.lesson-item-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}
.lesson-item-type {
  font-size: 11px;
  color: var(--text-tertiary);
}
.lesson-item-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6C5CE7;
  flex-shrink: 0;
}

.lesson-list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 0;
  color: var(--text-tertiary);
}
.lesson-list-empty p {
  margin: 0;
  font-size: 13px;
}

/* ===== Non-video sections ===== */
.non-video-section {
  margin-bottom: 20px;
}

.pdf-viewer,
.office-viewer {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border-default);
}
.pdf-frame {
  width: 100%;
  height: 600px;
  display: block;
}
.office-frame {
  width: 100%;
  height: 500px;
  display: block;
}

.doc-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 0;
  color: var(--text-tertiary);
}
.doc-placeholder p {
  margin: 0;
  font-size: 14px;
}

.doc-info-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-hover);
  border-radius: 10px;
  border: 1px solid var(--border-default);
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}
.doc-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unknown-placeholder {
  padding: 32px 0;
  text-align: center;
  color: var(--text-tertiary);
}
.unknown-placeholder p {
  margin: 0;
  font-size: 14px;
}

.action-bar {
  display: flex;
  justify-content: center;
  padding: 16px 0 0;
}

.text-body {
  line-height: 1.8;
  color: var(--text-primary);
  padding: 4px 0;
}

/* Markdown styles */
.markdown-body h1 { font-size: 24px; font-weight: 700; margin: 24px 0 12px; color: var(--text-primary); border-bottom: 1px solid var(--border-default); padding-bottom: 8px; }
.markdown-body h2 { font-size: 20px; font-weight: 700; margin: 20px 0 10px; color: var(--text-primary); }
.markdown-body h3 { font-size: 17px; font-weight: 600; margin: 16px 0 8px; color: var(--text-primary); }
.markdown-body h4 { font-size: 15px; font-weight: 600; margin: 12px 0 6px; color: var(--text-secondary); }
.markdown-body p { margin: 8px 0; line-height: 1.8; }
.markdown-body ul, .markdown-body ol { margin: 8px 0; padding-left: 24px; }
.markdown-body li { margin: 4px 0; line-height: 1.7; }
.markdown-body code {
  background: var(--bg-hover);
  color: #6C5CE7;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}
.markdown-body pre {
  background: #1a1a2e;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 12px 0;
  font-size: 14px;
  line-height: 1.6;
}
.markdown-body pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
}
.markdown-body blockquote {
  border-left: 4px solid #6C5CE7;
  padding: 8px 16px;
  margin: 12px 0;
  background: var(--bg-hover);
  border-radius: 0 8px 8px 0;
  color: var(--text-secondary);
}
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
.markdown-body th, .markdown-body td {
  padding: 8px 12px;
  border: 1px solid var(--border-default);
  text-align: left;
}
.markdown-body th {
  background: var(--bg-hover);
  font-weight: 600;
  color: var(--text-primary);
}
.markdown-body img {
  max-width: 100%;
  border-radius: 8px;
  margin: 12px 0;
}
.markdown-body a {
  color: #6C5CE7;
  text-decoration: none;
}
.markdown-body a:hover {
  text-decoration: underline;
}
.markdown-body hr {
  border: none;
  border-top: 1px solid var(--border-default);
  margin: 24px 0;
}

/* ===== Transitions ===== */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.scale-fade-enter-active, .scale-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.scale-fade-enter-from, .scale-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  opacity: 0;
  transform: translateY(16px);
}

/* ===== Responsive ===== */
@media (max-width: 960px) {
  .player-layout {
    flex-direction: column;
  }
  .player-sidebar {
    width: 100%;
    position: static;
    margin-top: 20px;
  }
  .lesson-list {
    max-height: 400px;
  }
}

@media (max-width: 640px) {
  .lesson-player {
    padding: 12px 12px 32px;
  }
  .lesson-meta-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .lesson-title {
    font-size: 16px;
  }
  .control-bar {
    padding: 32px 10px 8px;
  }
  .center-play-circle {
    width: 56px;
    height: 56px;
  }
  .controls-right {
    gap: 2px;
  }
  .volume-control {
    display: none;
  }
  .time-display {
    font-size: 11px;
  }
}
</style>
