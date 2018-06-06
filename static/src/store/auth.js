import globalAxios from 'axios'
import router from '../router'

const state = {
  idToken: null,
  user: null
}

const mutations = {
  authUser(state, userData) {
    state.idToken = userData.token
  },
  storeUser(state, user) {
    state.user = user
  },
  clearAuthData(state) {
    state.idToken = null
    state.user = null
  }
}

const actions = {
  login({ commit, dispatch }, authData) {
    globalAxios
      .post('/api/v1/login', {
        username: authData.email,
        password: authData.password
      })
      .then(res => {
        localStorage.setItem('token', res.data.jwt)
        commit('authUser', { token: res.data.jwt })
        dispatch('fetchUser')
      })
      .then(() => dispatch('loadVineyards'))
      .then(() => router.replace('/alerts'))
      .catch(error => console.log(error))
  },
  tryAutoLogin({ commit, dispatch }) {
    const token = localStorage.getItem('token')
    if (!token) {
      return
    }
    commit('authUser', { token: token })
    dispatch('fetchUser').then(() => {
      dispatch('loadVineyards')
    })
  },
  logout({ commit }) {
    commit('clearAuthData')
    localStorage.removeItem('token')
    router.replace('/')
  },
  fetchUser({ commit, state }) {
    if (!state.idToken) {
      return
    }
    const authHeader = {
      Authorization: 'Bearer ' + state.idToken
    }
    globalAxios
      .get('/api/v1/users', { headers: authHeader })
      .then(res => {
        const user = res.data
        commit('storeUser', user)
      })
      .catch(error => {
        console.log(error)
        router.replace('/')
      })
  }
}

const getters = {
  user(state) {
    return state.user
  },
  isAuthenticated(state) {
    return state.idToken !== null
  }
}

export default {
  state,
  mutations,
  getters,
  actions
}
