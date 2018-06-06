<template>
  <b-form-select v-model="selected" class="my-s2 my-lg-0">
    <option v-for="vineyard in vineyards" v-bind:key="vineyard.id">{{ vineyard.name }}</option>
  </b-form-select>
</template>

<script>
export default {
  name: 'VineyardSelector',
  data() {
    return {
      selected: null
    }
  },
  props: ['vineyards']
}
</script>

<style>
</style>
