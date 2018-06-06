<template>
  <div>
    <div class="tabs">
      <ul>
        <li>
          <router-link :to='{ name: "soil-stats" }' tag='li' active-class='is-active'>
            <a>Soil stats</a>
          </router-link>
        </li>
        <li>
          <router-link :to='{ name: "microclimate" }' tag='li' active-class='is-active'>
            <a>Microclimate</a>
          </router-link>
        </li>
        <li>
          <router-link :to='{ name: "weather" }' tag='li' active-class='is-active'>
            <a>Weather</a>
          </router-link>
        </li>
      </ul>
    </div>
    <router-view></router-view>
   </div>
</template>

<script>
export default {
  name: 'Vineyard'
}
</script>
