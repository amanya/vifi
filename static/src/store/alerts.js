import globalAxios from 'axios'
import router from '../router'

export default {
  state: {
    alerts: [],
    loading: false,
    error: false
  },
  getters: {
    unAckAlerts: state => {
      return state.alerts.filter(a => a.acknowledged === false).length > 0
    },
    numUnAckAlerts: state => {
      return state.alerts.filter(a => a.acknowledged === false).length
    }
  },
  mutations: {
    alertsFetchSuccess(state, alerts) {
      state.loading = false
      state.error = false
      state.alerts = alerts
    },
    alertsFetchError(state) {
      state.loading = false
      state.error = true
      state.alerts = []
    },
    alertAcknowledge(state, id) {
      state.alerts.filter(a => a.id === id)[0].acknowledged = true
    }
  },
  actions: {
    acknowledge({ commit }, id) {
      const authHeader = {
        Authorization: 'Bearer ' + this.state.auth.idToken
      }
      globalAxios.put('/api/v1/alerts/' + id, {}, { headers: authHeader }).then(response => {
        commit('alertAcknowledge', id)
      })
    },
    fetchAlerts({ commit }) {
      const authHeader = {
        Authorization: 'Bearer ' + this.state.auth.idToken
      }
      globalAxios
        .get('/api/v1/alerts/', { headers: authHeader })
        .then(response => response.data)
        .then(data => {
          commit(
            'alertsFetchSuccess',
            data.alerts.sort((a, b) => {
              if (a.created_at > b.created_at) return -1
              if (a.created_at < b.created_at) return 1
              return 0
            })
          )
        })
        .catch(error => {
          console.log(error)
          commit('alertsFetchError')
          commit('clearAuthData')
          localStorage.removeItem('token')
          router.replace('/')
        })
    }
  }
}
