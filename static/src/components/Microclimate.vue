<template>
  <div>
    <header>
      <h1 class="title">{{ vineyard.name }}'s microclimate</h1>
    </header>
  </div>
</template>
<script>
import { mapState } from 'vuex'
export default {
  name: 'Microclimate',
  computed: {
    ...mapState({
      vineyards: state => state.vineyards.vineyards
    }),
    vineyard() {
      return this.vineyards.filter(vineyard => vineyard.id === parseInt(this.$route.params.id))[0]
    }
  }
}
</script>
