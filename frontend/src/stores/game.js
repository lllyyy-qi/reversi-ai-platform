import { defineStore } from 'pinia'
import { ref } from 'vue'
import { gameAPI } from '@/services/api'

const INITIAL_BOARD = Array(8).fill().map(() => Array(8).fill(0))
INITIAL_BOARD[3][3] = 1
INITIAL_BOARD[4][4] = 1
INITIAL_BOARD[3][4] = -1
INITIAL_BOARD[4][3] = -1

export const useGameStore = defineStore('game', () => {
  const board = ref(JSON.parse(JSON.stringify(INITIAL_BOARD)))
  const currentPlayer = ref(-1)  // 黑先
  const legalMoves = ref([])
  const lastMove = ref(null)
  const gameOver = ref(false)
  const winner = ref(null)
  const moveHistory = ref([])
  const gameMode = ref('human')  // 'human' 或 'ai-vs-ai'

  // 计算棋子数量
  const pieceCount = () => {
    let black = 0, white = 0
    for (let i = 0; i < 8; i++) {
      for (let j = 0; j < 8; j++) {
        if (board.value[i][j] === -1) black++
        else if (board.value[i][j] === 1) white++
      }
    }
    return { black, white }
  }

// 重置游戏
const resetGame = async () => {
  board.value = JSON.parse(JSON.stringify(INITIAL_BOARD))
  currentPlayer.value = -1
  lastMove.value = null
  gameOver.value = false
  winner.value = null
  moveHistory.value = []
  legalMoves.value = []  // 先清空
  
  // 获取初始合法移动
  try {
    const res = await gameAPI.getLegalMoves(board.value, currentPlayer.value)
    legalMoves.value = res.data
    console.log('初始合法移动:', legalMoves.value)
  } catch (error) {
    console.error('获取初始合法移动失败', error)
  }
}

  // 保存当前状态快照
  const saveSnapshot = () => ({
    board: JSON.parse(JSON.stringify(board.value)),
    player: currentPlayer.value,
    lastMove: lastMove.value ? [...lastMove.value] : null,
    legalMoves: [...legalMoves.value],
    gameOver: gameOver.value,
    winner: winner.value
  })

// 执行玩家移动
const makeMove = async (row, col) => {
  if (gameOver.value) return false
  // 检查是否合法
  if (!legalMoves.value.some(m => m[0] === row && m[1] === col)) return false

  console.log('玩家尝试移动:', row, col, '当前玩家:', currentPlayer.value === -1 ? '黑' : '白')

  const snapshot = saveSnapshot()
  try {
    const response = await gameAPI.applyMove(board.value, currentPlayer.value, [row, col])
    // 更新状态
    board.value = response.data.board
    currentPlayer.value = -currentPlayer.value  // 切换到对方
    legalMoves.value = response.data.candidate_moves
    lastMove.value = [row, col]
    gameOver.value = response.data.game_over
    winner.value = response.data.winner
    // 保存历史
    moveHistory.value.push(snapshot)
    
    console.log('玩家移动后，当前玩家:', currentPlayer.value === -1 ? '黑' : '白')
    
    return true
  } catch (error) {
    console.error('移动失败', error)
    return false
  }
}
// AI 移动
const makeAIMove = async () => {
  if (gameOver.value) return false
  
  console.log('AI正在思考...', currentPlayer.value === -1 ? '黑棋' : '白棋', 
              '合法移动数:', legalMoves.value.length)
  
  const snapshot = saveSnapshot()
  try {
    const response = await gameAPI.getAIMove(board.value, currentPlayer.value)
    
    console.log('AI响应:', response.data)
    
    if (response.data.move) {
      // AI成功下棋
      board.value = response.data.board
      currentPlayer.value = -currentPlayer.value
      legalMoves.value = response.data.candidate_moves
      lastMove.value = response.data.move
      gameOver.value = response.data.game_over
      winner.value = response.data.winner
      moveHistory.value.push(snapshot)
      console.log('AI下棋完成，当前玩家:', currentPlayer.value === -1 ? '黑棋' : '白棋',
                  '合法移动数:', legalMoves.value.length)
      return true
    } else if (response.data.game_over) {
      gameOver.value = true
      winner.value = response.data.winner
      console.log('游戏结束，胜者:', winner.value)
      return false
    } else {
      // AI没有合法移动，自动跳过
      console.log('AI没有合法移动，自动跳过')
      
      // 保存跳过前的状态
      moveHistory.value.push(snapshot)
      
      // 切换玩家
      currentPlayer.value = -currentPlayer.value
      legalMoves.value = response.data.candidate_moves
      
      // 检查新玩家是否有合法移动
      if (legalMoves.value.length === 0) {
        // 双方都无合法移动，游戏结束
        const count = pieceCount()
        if (count.black < count.white) winner.value = -1
        else if (count.white < count.black) winner.value = 1
        else winner.value = 0
        gameOver.value = true
        console.log('双方都无合法移动，游戏结束')
      }
      
      return false
    }
  } catch (error) {
    console.error('AI移动失败', error)
    // 出错时恢复快照
    if (snapshot) {
      board.value = snapshot.board
      currentPlayer.value = snapshot.player
      lastMove.value = snapshot.lastMove
      legalMoves.value = snapshot.legalMoves
      gameOver.value = snapshot.gameOver
      winner.value = snapshot.winner
    }
    return false
  }
}

// 辅助函数：强制玩家移动
const makePlayerMove = async (row, col) => {
  console.log('强制移动:', row, col)
  const snapshot = saveSnapshot()
  try {
    const response = await gameAPI.applyMove(board.value, currentPlayer.value, [row, col])
    board.value = response.data.board
    currentPlayer.value = -currentPlayer.value
    legalMoves.value = response.data.candidate_moves
    lastMove.value = [row, col]
    gameOver.value = response.data.game_over
    winner.value = response.data.winner
    moveHistory.value.push(snapshot)
    return true
  } catch (error) {
    console.error('强制移动失败', error)
    return false
  }
}

// 悔棋 - 回退两步（玩家和AI各一步）
const undo = () => {
  console.log('===== 悔棋开始 =====')
  console.log('当前历史步数:', moveHistory.value.length)
  
  if (moveHistory.value.length < 2) {
    console.log('历史步数不足，不能悔棋')
    return false
  }
  
  // 记录悔棋前的状态
  console.log('悔棋前 - 当前玩家:', currentPlayer.value === -1 ? '黑棋' : '白棋')
  console.log('悔棋前 - 最后一步:', lastMove.value)
  
  // 回退两步
  const aiMoveState = moveHistory.value.pop() // 移除AI的移动
  const playerMoveState = moveHistory.value.pop() // 获取玩家移动前的状态
  
  console.log('移除的AI移动:', aiMoveState.lastMove)
  console.log('恢复到玩家移动前的状态:', playerMoveState)
  
  // 恢复到玩家移动前的状态
  board.value = playerMoveState.board
  currentPlayer.value = playerMoveState.player
  lastMove.value = playerMoveState.lastMove
  legalMoves.value = playerMoveState.legalMoves
  gameOver.value = playerMoveState.gameOver
  winner.value = playerMoveState.winner
  
  console.log('悔棋后 - 当前玩家:', currentPlayer.value === -1 ? '黑棋' : '白棋')
  console.log('悔棋后 - 合法移动:', legalMoves.value)
  console.log('===== 悔棋结束 =====')
  return true
}

// 跳过回合（当无合法移动时）
const pass = async () => {
  console.log('执行跳过，当前玩家:', currentPlayer.value === -1 ? '黑棋' : '白棋')
  
  if (legalMoves.value.length === 0 && !gameOver.value) {
    // 保存快照
    const snapshot = saveSnapshot()
    
    // 切换玩家
    currentPlayer.value = -currentPlayer.value
    console.log('切换到玩家:', currentPlayer.value === -1 ? '黑棋' : '白棋')
    
    try {
      // 获取新玩家的合法移动
      const res = await gameAPI.getLegalMoves(board.value, currentPlayer.value)
      legalMoves.value = res.data
      console.log('新玩家合法移动:', legalMoves.value.length)
      
      // 如果对方也无合法移动，游戏结束
      if (res.data.length === 0) {
        console.log('双方都无合法移动，游戏结束')
        // 计算胜负（反向黑白棋：少者胜）
        const count = pieceCount()
        if (count.black < count.white) winner.value = -1
        else if (count.white < count.black) winner.value = 1
        else winner.value = 0
        gameOver.value = true
      }
      
      // 记录历史
      moveHistory.value.push(snapshot)
      
      return true
    } catch (error) {
      console.error('获取合法移动失败', error)
      // 恢复快照
      board.value = snapshot.board
      currentPlayer.value = snapshot.player
      lastMove.value = snapshot.lastMove
      legalMoves.value = snapshot.legalMoves
      gameOver.value = snapshot.gameOver
      winner.value = snapshot.winner
      return false
    }
  } else {
    console.log('当前有合法移动，不能跳过')
    return false
  }
}
  // 保存游戏（后续实现）
  const saveGame = async (result) => {
    // TODO
  }

  return {
    board,
    currentPlayer,
    legalMoves,
    lastMove,
    gameOver,
    winner,
    moveHistory,
    gameMode,
    pieceCount,
    resetGame,
    makeMove,
    makeAIMove,
    undo,
    pass,
    saveGame
  }
})