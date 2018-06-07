<template>
  <div>
    <Navbar />
    <div class="columns is-fullheight">
      <div v-if="isAuthenticated" class="column is-2 is-sidebar-menu is-hidden-mobile">
        <aside v-if="loaded" class="menu">
          <p class="menu-label">
            General
          </p>
          <ul class="menu-list">
            <li>
              <router-link :to='{ name: "alerts" }' active-class='is-active'>
                Alerts
                <span v-if="unAckAlerts" class="badge is-badge-danger is-badge-medium" :data-badge="numUnAckAlerts"></span>
              </router-link>
            </li>
          </ul>
          <p class="menu-label">
            Vineyards
          </p>
          <ul class="menu-list">
            <li v-for="vineyard in vineyards" :key="vineyard.id">
              <router-link :to='{ name: "vineyard", params: { id: vineyard.id } }' active-class='is-active'>
                {{ vineyard.name }}
              </router-link>
            </li>
          </ul>
        </aside>
      </div>
      <div class="column is-main-content section">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar'
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'App',
  components: {
    Navbar
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

.columns
  &.is-fullheight
    min-height: calc(100vh - ( #{$navbar-height} - .75rem ) )
    max-height: calc(100vh - ( #{$navbar-height} - .75rem ) )
    height: calc(100vh - ( #{$navbar-height} - .75rem ) )
    display: flex
    flex-direction: row
    justify-content: stretch
    .column
      overflow-y: auto
</style>
