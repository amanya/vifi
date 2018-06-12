<template>
  <div>
    <navbar />
    <div class="columns">
      <aside v-if="isAuthenticated" class="column menu is-2 is-sidebar-menu is-hidden-mobile aside">
        <ul class="menu-list">
          <li>
            <router-link :to='{ name: "alerts" }' active-class='is-active'>
              Alerts
              <span v-if="unAckAlerts" class="badge is-badge-danger is-badge-medium" :data-badge="numUnAckAlerts"></span>
            </router-link>
          </li>
          <li>
            <router-link :to='{ name: "health-stats" }' active-class='is-active'>
              Health status
            </router-link>
          </li>
          <li>
            <router-link :to='{ name: "soil-stats" }'>
              Soil stats
            </router-link>
            <ul>
              <li v-for="vineyard in vineyards" :key="vineyard.id">
                <router-link :to='{ name: "soil-stats", params: { id: vineyard.id } }' active-class='is-active'>
                  {{ vineyard.name }}
                </router-link>
              </li>
            </ul>
          </li>
          <li>
            <router-link :to='{ name: "microclimate" }'>
              Microclimate
            </router-link>
            <ul>
              <li v-for="vineyard in vineyards" :key="vineyard.id">
                <router-link :to='{ name: "microclimate", params: { id: vineyard.id } }' active-class='is-active'>
                  {{ vineyard.name }}
                </router-link>
              </li>
            </ul>
          </li>
          <li>
            <router-link :to='{ name: "weather" }'>
              Weather
            </router-link>
            <ul>
              <li v-for="vineyard in vineyards" :key="vineyard.id">
                <router-link :to='{ name: "weather", params: { id: vineyard.id } }' active-class='is-active'>
                  {{ vineyard.name }}
                </router-link>
              </li>
            </ul>
          </li>
        </ul>
      </aside>
      <div class="column is-main-content is-10 section">
        <router-view />
      </div>
    </div>
    <foot />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar'
import Foot from '@/components/Foot'
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'App',
  components: {
    Navbar,
    Foot
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'isAuthenticated',
      unAckAlerts: 'unAckAlerts',
      numUnAckAlerts: 'numUnAckAlerts'
    }),
    ...mapState({
      loaded: state => state.vineyards.loaded,
      vineyards: state => state.vineyards.vineyards
    })
  },
  created() {
    if (this.isAuthenticated) {
      setInterval(
        function() {
          this.$store.dispatch('fetchAlerts')
        }.bind(this),
        10000
      )
    }
  }
}
</script>

<style lang="sass">

$navbar-height: 3.25rem

.is-sidebar-menu
  padding: 2.5rem

</style>
