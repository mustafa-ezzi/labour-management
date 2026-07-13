<template>
  <Teleport to="body">
    <Transition name="tour-fade">
      <div v-if="active" class="fixed inset-0 z-[200]">
        <!-- Full dim backdrop: welcome/closing steps or before target is located -->
        <div v-if="!box" class="fixed inset-0 bg-[#150a28]/60 backdrop-blur-[3px]" />

        <template v-else>
          <div class="tour-mask fixed bg-[#150a28]/60 backdrop-blur-[3px]" :style="pieceTop" />
          <div class="tour-mask fixed bg-[#150a28]/60 backdrop-blur-[3px]" :style="pieceBottom" />
          <div class="tour-mask fixed bg-[#150a28]/60 backdrop-blur-[3px]" :style="pieceLeft" />
          <div class="tour-mask fixed bg-[#150a28]/60 backdrop-blur-[3px]" :style="pieceRight" />
          <!-- Transparent guard over the spotlight hole: blocks clicks without dimming it -->
          <div class="tour-mask fixed z-[1]" :style="holeStyle" />
          <div class="tour-ring fixed z-[2] rounded-2xl border-2 border-violet-300/90" :style="holeStyle" />
        </template>

        <div
          v-if="currentStep"
          ref="tooltipRef"
          class="tour-pop fixed z-[3] w-[min(340px,calc(100vw-32px))] rounded-[20px] border border-white/60 bg-gradient-to-br from-white/85 to-violet-100/65 p-4 pb-4 shadow-[0_24px_60px_-12px_rgba(59,7,100,0.45)] backdrop-blur-2xl backdrop-saturate-150"
          :style="cardStyle"
        >
          <span
            v-if="box"
            class="absolute h-3.5 w-3.5 rotate-45 border border-white/60 bg-gradient-to-br from-white/90 to-violet-100/70"
            :class="arrowClass"
          />

          <button
            type="button"
            class="absolute right-3 top-3 flex h-7 w-7 items-center justify-center rounded-full text-gray-400 transition-colors hover:bg-white/70 hover:text-gray-700"
            aria-label="Close tour"
            @click="skip"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div class="flex items-center gap-2 pr-6">
            <span
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-violet-700 text-white shadow-md shadow-violet-700/30"
            >
              <AppNavIcon :name="currentStep.icon || 'home'" class="h-4 w-4" />
            </span>
            <p class="text-[10px] font-bold uppercase tracking-wider text-violet-600">
              Step {{ stepIndex + 1 }} of {{ steps.length }}
            </p>
          </div>

          <h3 class="mt-3 text-base font-bold text-gray-900">{{ currentStep.title }}</h3>
          <p class="mt-1.5 text-sm leading-relaxed text-gray-700">{{ currentStep.description }}</p>

          <div class="mt-4 flex items-center justify-center gap-1.5">
            <span
              v-for="(s, i) in steps"
              :key="s.id"
              class="h-1.5 rounded-full transition-all duration-300"
              :class="i === stepIndex ? 'w-5 bg-violet-600' : 'w-1.5 bg-violet-200'"
            />
          </div>

          <div class="mt-4 flex items-center gap-2">
            <button
              v-if="!isFirst"
              type="button"
              class="rounded-lg px-3 py-2 text-xs font-semibold text-gray-500 transition-colors hover:bg-white/60"
              @click="prev"
            >
              Back
            </button>
            <button
              type="button"
              class="mr-auto rounded-lg px-2 py-2 text-xs font-medium text-gray-400 underline-offset-2 hover:text-gray-600 hover:underline"
              @click="skip"
            >
              Skip tour
            </button>
            <button
              type="button"
              class="rounded-lg bg-violet-700 px-4 py-2 text-xs font-bold text-white shadow-md shadow-violet-700/30 transition-all hover:bg-violet-600 active:scale-95"
              @click="next"
            >
              {{ isLast ? 'Finish' : 'Next' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const { active, steps, stepIndex, currentStep, isFirst, isLast, ready, targetRect, next, prev, skip, refreshRect } =
  useOnboardingTour()

const PADDING = 10
const RADIUS = 16

const tooltipRef = ref<HTMLElement | null>(null)
const placement = ref<'top' | 'bottom' | 'left' | 'right'>('bottom')
const cardPos = reactive({ top: 0, left: 0 })

const box = computed(() => {
  if (!ready.value || !targetRect.value) return null
  const r = targetRect.value
  if (r.width <= 0 || r.height <= 0) return null
  return {
    top: r.top - PADDING,
    left: r.left - PADDING,
    width: r.width + PADDING * 2,
    height: r.height + PADDING * 2,
  }
})

const pieceTop = computed(() => {
  const b = box.value
  if (!b) return {}
  return { top: '0px', left: '0px', right: '0px', height: `${Math.max(b.top, 0)}px` }
})
const pieceBottom = computed(() => {
  const b = box.value
  if (!b) return {}
  return { top: `${b.top + b.height}px`, left: '0px', right: '0px', bottom: '0px' }
})
const pieceLeft = computed(() => {
  const b = box.value
  if (!b) return {}
  return { top: `${b.top}px`, height: `${b.height}px`, left: '0px', width: `${Math.max(b.left, 0)}px` }
})
const pieceRight = computed(() => {
  const b = box.value
  if (!b) return {}
  return { top: `${b.top}px`, height: `${b.height}px`, left: `${b.left + b.width}px`, right: '0px' }
})
const holeStyle = computed(() => {
  const b = box.value
  if (!b) return {}
  return {
    top: `${b.top}px`,
    left: `${b.left}px`,
    width: `${b.width}px`,
    height: `${b.height}px`,
    borderRadius: `${RADIUS}px`,
  }
})

const arrowClass = computed(() => {
  switch (placement.value) {
    case 'bottom':
      return '-top-[7px] left-1/2 -translate-x-1/2 border-b-0 border-r-0'
    case 'top':
      return '-bottom-[7px] left-1/2 -translate-x-1/2 border-t-0 border-l-0'
    case 'right':
      return '-left-[7px] top-1/2 -translate-y-1/2 border-r-0 border-t-0'
    default:
      return '-right-[7px] top-1/2 -translate-y-1/2 border-l-0 border-b-0'
  }
})

const cardStyle = computed(() => ({
  top: `${cardPos.top}px`,
  left: `${cardPos.left}px`,
}))

function computePlacementAndPosition() {
  const b = box.value
  const el = tooltipRef.value
  if (!b || !el) return
  const vw = window.innerWidth
  const vh = window.innerHeight
  const margin = 16
  const tw = el.offsetWidth
  const th = el.offsetHeight

  const targetCenterX = b.left + b.width / 2
  const targetBottom = b.top + b.height
  const spaceBelow = vh - targetBottom
  const spaceAbove = b.top
  const spaceRight = vw - (b.left + b.width)
  const spaceLeft = b.left

  const order: Array<['bottom' | 'top' | 'right' | 'left', number]> = [
    ['bottom', spaceBelow],
    ['top', spaceAbove],
    ['right', spaceRight],
    ['left', spaceLeft],
  ]
  const withRoom = order.filter(([dir, space]) =>
    dir === 'bottom' || dir === 'top' ? space > th + 24 : space > tw + 24,
  )
  let chosen: 'top' | 'bottom' | 'left' | 'right'
  if (withRoom.length) {
    withRoom.sort((a, b2) => b2[1] - a[1])
    chosen = withRoom[0][0]
  } else {
    const fallback = [...order].sort((a, b2) => b2[1] - a[1])
    chosen = fallback[0][0]
  }

  if (vw < 640 && (chosen === 'left' || chosen === 'right')) {
    chosen = spaceBelow >= spaceAbove ? 'bottom' : 'top'
  }

  placement.value = chosen

  let top = 0
  let left = 0
  if (chosen === 'bottom') {
    top = targetBottom + 18
    left = targetCenterX - tw / 2
  } else if (chosen === 'top') {
    top = b.top - th - 18
    left = targetCenterX - tw / 2
  } else if (chosen === 'right') {
    top = b.top + b.height / 2 - th / 2
    left = b.left + b.width + 18
  } else {
    top = b.top + b.height / 2 - th / 2
    left = b.left - tw - 18
  }

  cardPos.left = Math.min(Math.max(left, margin), vw - tw - margin)
  cardPos.top = Math.min(Math.max(top, margin), vh - th - margin)
}

function computeCenteredPosition() {
  const el = tooltipRef.value
  if (!el) return
  const vw = window.innerWidth
  const vh = window.innerHeight
  cardPos.top = Math.max(16, vh / 2 - el.offsetHeight / 2)
  cardPos.left = Math.max(16, vw / 2 - el.offsetWidth / 2)
}

async function reposition() {
  await nextTick()
  if (box.value) computePlacementAndPosition()
  else computeCenteredPosition()
}

watch([box, currentStep], () => {
  reposition()
})

function onResize() {
  refreshRect()
  reposition()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') skip()
  else if (e.key === 'ArrowRight') next()
  else if (e.key === 'ArrowLeft') prev()
}

watch(active, (isActive) => {
  if (!import.meta.client) return
  document.body.classList.toggle('tour-open', isActive)
  if (isActive) {
    window.addEventListener('keydown', onKeydown)
    reposition()
  } else {
    window.removeEventListener('keydown', onKeydown)
  }
})

onMounted(() => {
  window.addEventListener('resize', onResize)
  if (active.value) reposition()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  if (import.meta.client) {
    document.body.classList.remove('tour-open')
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<style>
.tour-mask,
.tour-ring {
  transition:
    top 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    left 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    right 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    bottom 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    width 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    height 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.tour-ring {
  box-shadow:
    0 0 0 4px rgba(124, 58, 237, 0.22),
    0 0 30px 4px rgba(124, 58, 237, 0.45);
  animation: tour-pulse-ring 2.2s ease-in-out infinite;
}

@keyframes tour-pulse-ring {
  0%,
  100% {
    box-shadow:
      0 0 0 4px rgba(124, 58, 237, 0.22),
      0 0 30px 4px rgba(124, 58, 237, 0.45);
  }
  50% {
    box-shadow:
      0 0 0 8px rgba(124, 58, 237, 0.12),
      0 0 42px 10px rgba(124, 58, 237, 0.6);
  }
}

.tour-pop {
  animation: tour-pop-in 0.24s cubic-bezier(0.22, 1, 0.36, 1);
  transition:
    top 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    left 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes tour-pop-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(4px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.tour-fade-enter-active,
.tour-fade-leave-active {
  transition: opacity 0.25s ease;
}
.tour-fade-enter-from,
.tour-fade-leave-to {
  opacity: 0;
}
</style>
