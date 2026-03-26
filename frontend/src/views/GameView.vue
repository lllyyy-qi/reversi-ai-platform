<template>
  <div class="game-view">
    <div class="game-container">
      <Board
        :board="gameStore.board"
        :legalMoves="gameStore.legalMoves"
        :lastMove="gameStore.lastMove"
        @cell-click="handleCellClick"
      />
      
      <GameControls
        :currentPlayer="gameStore.currentPlayer"
        :pieceCount="gameStore.pieceCount()"
        :canPass="gameStore.legalMoves.length === 0 && !gameStore.gameOver"
        :canUndo="gameStore.moveHistory.length > 0"
        :mode="gameStore.gameMode"
        @new-game="handleNewGame"
        @pass="handlePass"
        @undo="handleUndo"
        @mode-change="handleModeChange"
      />
    </div>
    
    <div v-if="gameStore.gameOver" class="game-over-modal">
      <div class="modal-content">
        <h2>游戏结束</h2>
        <p class="winner">{{ winnerText }}</p>
        <div class="final-score">
          <span>黑: {{ gameStore.pieceCount().black }}</span>
          <span>白: {{ gameStore.pieceCount().white }}</span>
        </div>
        <button @click="handleNewGame" class="btn btn-primary">再来一局</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, onMounted, onUnmounted, ref } from 'vue'
import { useGameStore } from '@/stores/game'
import Board from '@/components/Board.vue'
import GameControls from '@/components/GameControls.vue'

const gameStore = useGameStore()
const aiRunning = ref(false)
const aiLoopInterval = ref(null)

const winnerText = computed(() => {
  if (gameStore.winner === -1) return '黑方胜利！'
  if (gameStore.winner === 1) return '白方胜利！'
  if (gameStore.winner === 0) return '平局！'
  return ''
})

// 处理新游戏
async function handleNewGame() {
  console.log('===== 开始新游戏 =====')
  
  // 停止AI循环
  if (aiLoopInterval.value) {
    clearTimeout(aiLoopInterval.value)
    aiLoopInterval.value = null
  }
  aiRunning.value = false
  
  // 重置游戏状态
  await gameStore.resetGame()
  
  // 如果当前是AI观战模式，自动启动AI对战
  if (gameStore.gameMode === 'ai-vs-ai') {
    console.log('AI观战模式，启动AI对战')
    setTimeout(() => {
      runAIVersusAI()
    }, 500)
  }
}

async function handleCellClick(row, col) {
  if (gameStore.gameMode === 'human' && !aiRunning.value) {
    const moveMade = await gameStore.makeMove(row, col)
    if (moveMade && !gameStore.gameOver) {
      // 玩家移动后，如果轮到AI（白棋），则AI移动
      if (gameStore.currentPlayer === 1) {
        console.log('玩家移动后轮到AI，自动触发AI移动')
        aiRunning.value = true
        await gameStore.makeAIMove()
        aiRunning.value = false
      }
    }
  }
}

async function handlePass() {
  if (!aiRunning.value) {
    console.log('玩家点击跳过，当前玩家:', gameStore.currentPlayer === -1 ? '黑' : '白')
    await gameStore.pass()
    console.log('跳过后，当前玩家:', gameStore.currentPlayer === -1 ? '黑' : '白')
    
    // 如果是人机模式且跳过后轮到AI，自动触发AI移动
    if (gameStore.gameMode === 'human' && gameStore.currentPlayer === 1 && !gameStore.gameOver) {
      console.log('跳过后轮到AI，自动触发AI移动')
      aiRunning.value = true
      await gameStore.makeAIMove()
      aiRunning.value = false
    }
  }
}

function handleUndo() {
  if (!aiRunning.value) {
    gameStore.undo()
  }
}

function handleModeChange(mode) {
  // 停止当前AI循环
  if (aiLoopInterval.value) {
    clearTimeout(aiLoopInterval.value)
    aiLoopInterval.value = null
  }
  aiRunning.value = false
  
  // 切换模式
  gameStore.gameMode = mode
  gameStore.resetGame()
  
  // 如果是AI观战模式，启动AI对战
  if (mode === 'ai-vs-ai') {
    setTimeout(() => {
      runAIVersusAI()
    }, 500)
  }
}

// AI 对战自动循环 - 使用递归而不是while循环，避免阻塞
async function runAIVersusAI() {
  // 检查是否应该继续
  if (aiRunning.value) return
  if (gameStore.gameMode !== 'ai-vs-ai') return
  if (gameStore.gameOver) return
  
  aiRunning.value = true
  console.log('AI对战开始')
  
  // 使用递归函数，每次移动后等待
  const makeNextMove = async () => {
    // 检查是否应该继续
    if (gameStore.gameMode !== 'ai-vs-ai' || gameStore.gameOver || !aiRunning.value) {
      console.log('AI对战结束')
      aiRunning.value = false
      return
    }
    
    console.log('AI观战 - 当前玩家:', gameStore.currentPlayer === -1 ? '黑棋' : '白棋')
    
    // 执行AI移动
    const moveMade = await gameStore.makeAIMove()
    
    // 等待一段时间再继续
    if (!gameStore.gameOver && gameStore.gameMode === 'ai-vs-ai') {
      aiLoopInterval.value = setTimeout(() => {
        makeNextMove()
      }, 500)
    } else {
      aiRunning.value = false
    }
  }
  
  // 开始第一次移动
  makeNextMove()
}

// 监听模式变化
watch(() => gameStore.gameMode, (newMode, oldMode) => {
  if (newMode === 'ai-vs-ai' && oldMode !== 'ai-vs-ai') {
    // 启动新循环
    setTimeout(() => {
      runAIVersusAI()
    }, 500)
  } else if (newMode !== 'ai-vs-ai') {
    // 停止循环
    if (aiLoopInterval.value) {
      clearTimeout(aiLoopInterval.value)
      aiLoopInterval.value = null
    }
    aiRunning.value = false
  }
})

// 组件卸载时停止AI
onUnmounted(() => {
  if (aiLoopInterval.value) {
    clearTimeout(aiLoopInterval.value)
    aiLoopInterval.value = null
  }
  aiRunning.value = false
})

// 初始化
onMounted(() => {
  gameStore.resetGame()
})
</script>

<style scoped>
/* 样式保持不变 */
.game-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.game-container {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.game-over-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: modal-appear 0.3s ease-out;
}

@keyframes modal-appear {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.winner {
  font-size: 1.5em;
  margin: 20px 0;
  color: #333;
}

.final-score {
  display: flex;
  gap: 40px;
  justify-content: center;
  font-size: 1.2em;
  margin-bottom: 30px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}
</style>