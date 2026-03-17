<template>
  <div class="game-controls">
    <div class="game-status">
      <div class="current-player" :class="{ 'black-turn': currentPlayer === -1, 'white-turn': currentPlayer === 1 }">
        {{ currentPlayer === -1 ? '● 黑方回合' : '○ 白方回合' }}
      </div>
      <div class="piece-count">
        <div class="black-count">● 黑: {{ pieceCount.black }}</div>
        <div class="white-count">○ 白: {{ pieceCount.white }}</div>
      </div>
    </div>
    
    <div class="control-buttons">
      <button @click="$emit('new-game')" class="btn btn-primary">新游戏</button>
      <button @click="$emit('pass')" class="btn btn-secondary" :disabled="!canPass">跳过</button>
      <button @click="$emit('undo')" class="btn btn-secondary" :disabled="!canUndo">悔棋</button>
    </div>
    
    <div class="game-mode-selector" v-if="showModeSelector">
      <label>
        <input type="radio" value="human" v-model="gameMode" @change="$emit('mode-change', gameMode)" />
        人机对战
      </label>
      <label>
        <input type="radio" value="ai-vs-ai" v-model="gameMode" @change="$emit('mode-change', gameMode)" />
        AI观战
      </label>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPlayer: {
    type: Number,
    required: true
  },
  pieceCount: {
    type: Object,
    required: true,
    default: () => ({ black: 2, white: 2 })
  },
  canPass: {
    type: Boolean,
    default: false
  },
  canUndo: {
    type: Boolean,
    default: false
  },
  showModeSelector: {
    type: Boolean,
    default: true
  },
  mode: {
    type: String,
    default: 'human'
  }
})

const emit = defineEmits(['new-game', 'pass', 'undo', 'mode-change'])

const gameMode = computed({
  get: () => props.mode,
  set: (value) => emit('mode-change', value)
})
</script>

<style scoped>
.game-controls {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.game-status {
  text-align: center;
  margin-bottom: 20px;
}

.current-player {
  font-size: 1.2em;
  font-weight: bold;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 10px;
  transition: all 0.3s;
}

.black-turn {
  background: linear-gradient(135deg, #333, #000);
  color: white;
}

.white-turn {
  background: linear-gradient(135deg, #fff, #eee);
  color: black;
}

.piece-count {
  display: flex;
  justify-content: space-around;
  font-size: 1.1em;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
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
  background: linear-gradient(135deg, #ff6b6b, #ee5253);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.game-mode-selector {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.game-mode-selector label {
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.game-mode-selector label:hover {
  background: rgba(255, 255, 255, 0.2);
}

.game-mode-selector input {
  margin-right: 5px;
}
</style>