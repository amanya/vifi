<template>
  <nav class="navbar has-shadow is-spaced" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
      <p class="is-size-4 has-text-weight-bold"><a class="navbar-item" href="/">SenseEarth</a></p>
      <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false">
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>
    <div class="navbar-menu">
      <div class="navbar-end">
        <div v-if="user" class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link" href="#">
            {{ user.email }}
          </a>
          <div class="navbar-dropdown is-boxed">
            <router-link v-if="user.admin" :to='{ name: "api-tokens" }' class="navbar-item">
              API Tokens
            </router-link>
            <a class="navbar-item" href="#" @click="onLogout">Logout</a>
          </div>
        </div>
        <div v-if="false" class="navbar-item">
          <div class="select">
            <select v-model="selected">
              <option v-for="vineyard in vineyards" :key="vineyard.id" :value=vineyard>{{ vineyard.name }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
<script>
import { mapGetters, mapState } from 'vuex'

export default {
  name: 'Navbar',
  data() {
    return {
      showVineyardsSelect: false
    }
  },
  computed: {
    ...mapGetters({
      user: 'user'
    }),
    ...mapState({
      vineyards: state => state.vineyards.vineyards,
      selectedVineyard: state => state.vineyards.selectedVineyard
    }),
    selected: {
      get: function() {
        return this.selectedVineyard
      },
      set: function(newSelectedVineyard) {
        this.$store.dispatch('setSelectedVineyard', newSelectedVineyard)
      }
    }
  },
  methods: {
    onLogout() {
      this.$store.dispatch('logout')
    }
  }
}
</script>

<style lang="sass">
.title
  margin: 0
</style>
