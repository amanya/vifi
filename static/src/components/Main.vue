<template>
  <div>
    <Navbar />
    <div class="columns is-fullheight">
      <div v-if="isAuthenticated" class="column is-2 is-sidebar-menu is-hidden-mobile">
        <aside class="menu">
          <ul class="menu-list">
            <li>
              <router-link :to='{ name: "alerts" }' active-class='is-active'>
                Alerts
              </router-link>
            </li>
            <li>
              <router-link :to='{ name: "health-stats" }' active-class='is-active'>
                Health stats
              </router-link>
            </li>
            <li>
              <a class="id-disabled">
                Soil stats
              </a>
              <ul>
                <li v-for="vineyard in vineyards" :key="vineyard.id">
                  <router-link :to='{ name: "soil-stats", params: { id: vineyard.id } }' active-class='is-active'>
                    {{ vineyard.name }}
                  </router-link>
                </li>
              </ul>
            </li>
            <li>
              <router-link :to='{ name: "microclimate" }' active-class='is-active'>
                Microclimate
              </router-link>
            </li>
            <li>
              <router-link :to='{ name: "weather" }' active-class='is-active'>
                Weather
              </router-link>
            </li>
          </ul>
        </aside>
      </div>
      <div class="column is-main-content section">
        <router-view />
      </div>
    </div>
    <Foot></Foot>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar'
import Foot from '@/components/Foot'
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'Main',
  components: {
    Navbar,
    Foot
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'isAuthenticated'
    }),
    ...mapState({
      loaded: state => state.vineyards.loaded,
      vineyards: state => state.vineyards.vineyards
    })
  },
  created() {
    console.log('pupa')
    this.$store.dispatch('tryAutoLogin')
    if (!this.loaded) {
      this.$store.dispatch('loadVineyards')
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
