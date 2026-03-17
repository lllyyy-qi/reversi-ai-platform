<template>
  <div class="board-wrapper">
    <!-- 棋盘主体 -->
    <div class="board-container">
      <!-- 行号（左侧） -->
      <div class="row-numbers">
        <div v-for="i in 8" :key="i" class="row-number">{{ i }}</div>
      </div>
      
      <!-- 棋盘和列号 -->
      <div class="board-with-col-labels">
        <!-- 棋盘 -->
        <div class="board" :style="boardStyle">
          <div
            v-for="(row, i) in board"
            :key="i"
            class="board-row"
          >
            <div
              v-for="(cell, j) in row"
              :key="`${i}-${j}`"
              class="board-cell"
              :class="{
                'black-cell': cell === -1,
                'white-cell': cell === 1,
                'empty-cell': cell === 0,
                'legal-move': isLegalMove(i, j),
                'last-move': isLastMove(i, j)
              }"
              @click="onCellClick(i, j)"
            >
              <div class="piece" v-if="cell !== 0">
                <div class="piece-inner"></div>
              </div>
              <div v-if="isLegalMove(i, j) && showLegalMoves" class="legal-move-indicator"></div>
            </div>
          </div>
        </div>
        
        <!-- 列号（底部） -->
        <div class="col-letters">
          <div v-for="i in 8" :key="i" class="col-letter">
            {{ String.fromCharCode(64 + i) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  board: {
    type: Array,
    required: true,
    default: () => Array(8).fill().map(() => Array(8).fill(0))
  },
  legalMoves: {
    type: Array,
    default: () => []
  },
  lastMove: {
    type: Array,
    default: null
  },
  showLegalMoves: {
    type: Boolean,
    default: true
  },
  cellSize: {
    type: Number,
    default: 60
  }
})

const emit = defineEmits(['cell-click'])

const boardStyle = computed(() => ({
  width: `${props.cellSize * 8}px`,
  height: `${props.cellSize * 8}px`,
  display: 'grid',
  gridTemplateColumns: `repeat(8, ${props.cellSize}px)`
}))

function isLegalMove(row, col) {
  return props.legalMoves.some(move => move[0] === row && move[1] === col)
}

function isLastMove(row, col) {
  return props.lastMove && props.lastMove[0] === row && props.lastMove[1] === col
}

function onCellClick(row, col) {
  emit('cell-click', row, col)
}
</script>

<style scoped>
.board-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.board-container {
  display: flex;
  gap: 10px;
}

.row-numbers {
  display: flex;
  flex-direction: column;
  margin-top: 0;
}

.row-number {
  width: 30px;
  height: v-bind('cellSize + "px"');
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #333;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  margin-bottom: 2px;
}

.board-with-col-labels {
  display: flex;
  flex-direction: column;
}

.board {
  background-color: #2e5c2e;
  border: 2px solid #1e3c1e;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.board-row {
  display: contents;
}

.board-cell {
  position: relative;
  width: v-bind('cellSize + "px"');
  height: v-bind('cellSize + "px"');
  border: 1px solid #1e3c1e;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.empty-cell {
  background-color: #2e8b57;
}

.empty-cell:hover {
  background-color: #3cb371;
}

.piece {
  width: 80%;
  height: 80%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  animation: piece-appear 0.3s ease-out;
}

@keyframes piece-appear {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.black-cell .piece {
  background: radial-gradient(circle at 30% 30%, #666, #222);
}

.white-cell .piece {
  background: radial-gradient(circle at 30% 30%, #fff, #ddd);
}

.legal-move-indicator {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.3);
  pointer-events: none;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

.last-move {
  outline: 3px solid gold;
  outline-offset: -3px;
  z-index: 1;
}

.col-letters {
  display: flex;
  margin-top: 5px;
  gap: 2px;
}

.col-letter {
  width: v-bind('cellSize + "px"');
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #333;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
}
</style>