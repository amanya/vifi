import Vue from 'vue'
import Router from 'vue-router'

import Login from '@/components/Login'
import Alerts from '@/components/Alerts'
import HealthStats from '@/components/HealthStats'
import SoilStats from '@/components/SoilStats'
import Microclimate from '@/components/Microclimate'
import Weather from '@/components/Weather'
import Vineyard from '@/components/Vineyard'
import Logout from '@/components/Logout'
import VineyardDefault from '@/components/VineyardDefault'
import ApiTokens from '@/components/ApiTokens'

import store from '../store'

Vue.use(Router)

function checkAuth(to, from, next) {
  if (!store.getters.isAuthenticated) {
    store.dispatch('tryAutoLogin')
    next()
  } else {
    next()
  }
}

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Login',
      component: Login,
      beforeEnter(to, from, next) {
        if (store.state.auth.idToken) {
          next('alerts')
        } else {
          next()
        }
      }
    },
    {
      path: '/api-tokens',
      name: 'api-tokens',
      component: ApiTokens,
      beforeEnter: checkAuth
    },
    {
      path: '/alerts',
      name: 'alerts',
      component: Alerts,
      beforeEnter: checkAuth
    },
    {
      path: '/health-stats',
      name: 'health-stats',
      component: HealthStats,
      beforeEnter: checkAuth
    },
    {
      path: '/vineyard/:id',
      component: Vineyard,
      beforeEnter: checkAuth,
      children: [
        {
          path: '',
          name: 'vineyard',
          component: VineyardDefault,
          beforeEnter: checkAuth
        },
        {
          path: 'soil-stats',
          name: 'soil-stats',
          component: SoilStats,
          beforeEnter: checkAuth
        },
        {
          path: 'microclimate',
          name: 'microclimate',
          component: Microclimate,
          beforeEnter: checkAuth
        },
        {
          path: 'weather',
          name: 'weather',
          component: Weather,
          beforeEnter: checkAuth
        }
      ]
    },
    {
      path: '/logout',
      name: 'logout',
      component: Logout
    }
  ]
})
