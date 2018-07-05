import globalAxios from 'axios'
import router from '../router'

export default {
  state: {
    apiTokens: [],
    loading: false,
    error: false
  },
  mutations: {
    apiTokensFetchSuccess(state, apiTokens) {
      state.loading = false
      state.error = false
      state.apiTokens = apiTokens
    },
    apiTokensFetchError(state, apiTokens) {
      state.loading = false
      state.error = true
      state.apiTokens = []
    }
  },
  actions: {
    fetchApiTokens({ commit }) {
      const authHeader = {
        Authorization: 'Bearer ' + this.state.auth.idToken
      }
      globalAxios
        .get('/api/v1/api-tokens/', { headers: authHeader })
        .then(response => response.data)
        .then(data => {
          commit(
            'apiTokensFetchSuccess',
            data['api-tokens'].sort((a, b) => {
              if (a.timestamp > b.timestamp) return -1
              if (a.timestamp < b.timestamp) return 1
              return 0
            })
          )
        })
        .catch(error => {
          console.log(error)
          commit('apiTokensFetchError')
          commit('clearAuthData')
          localStorage.removeItem('token')
          router.replace('/')
        })
    }
  }
}
