<template>
  <div>
    <gmap-map
      v-if="google && vineyard"
      :center="center"
      :zoom="17"
      map-type-id="satellite"
      style="width: 100%; height: 400px"
      >
        <gmap-info-window
          v-for="(m, index) in markers"
          :key="`sensor-${index}`"
          :options="infoOptions"
          :position="infoWindowPos"
          :opened="infoWinOpen[index]"
          @closeclick="toggleInfoWindow(m, index)">
          <sensor-modal :sensor="m.sensor"/>
        </gmap-info-window>
        <gmap-marker
          v-for="(m, index) in markers"
          :key="`marker-${index}`"
          :position="m.position"
          :clickable="true"
          :draggable="false"
          @click="toggleInfoWindow(m, index)"
          />
    </gmap-map>
  </div>
</template>

<script>
import { gmapApi } from 'vue2-google-maps'
import SensorModal from './SensorModal'

export default {
  name: 'VineyardMap',
  props: ['vineyard'],
  components: {
    sensorModal: SensorModal
  },
  data() {
    return {
      zoom: 17,
      infoContent: '',
      infoWindowPos: null,
      infoWinOpen: {},
      currentMidx: null,
      currentSensor: null,
      infoOptions: {
        pixelOffset: {
          width: 0,
          height: -35
        }
      }
    }
  },
  created() {
    console.log(this.vineyard.sensors)
  },
  computed: {
    google: gmapApi,
    markers() {
      return this.getMarkers()
    },
    center() {
      if (this.google) {
        let bound = new this.google.maps.LatLngBounds()
        for (let i = 0; i < this.vineyard.sensors.length; i++) {
          bound.extend(
            new this.google.maps.LatLng(this.vineyard.sensors[i].latitude, this.vineyard.sensors[i].longitude)
          )
        }
        return bound.getCenter()
      }
    }
  },
  methods: {
    getMarkers() {
      let markers = []
      if (this.google && this.vineyard.sensors) {
        for (let i = 0; i < this.vineyard.sensors.length; i++) {
          markers.push({
            position: new this.google.maps.LatLng(
              this.vineyard.sensors[i].latitude,
              this.vineyard.sensors[i].longitude
            ),
            infoText: this.vineyard.sensors[i].description,
            sensor: this.vineyard.sensors[i]
          })
        }
      }
      let infoWinOpen = {}
      markers.forEach((m, idx) => {
        infoWinOpen[idx] = false
      })
      this.infoWinOpen = Object.assign({}, this.infoWinOpen, infoWinOpen)
      return markers
    },
    toggleInfoWindow: function(marker, idx) {
      this.infoWindowPos = marker.position
      this.infoContent = marker.infoText
      this.currentSensor = marker.sensor

      if (this.currentMidx === `sensor-${idx}`) {
        this.infoWinOpen[idx] = !this.infoWinOpen[idx]
      } else {
        this.vineyard.sensors.forEach((m, idx) => {
          this.infoWinOpen[idx] = false
        })
        this.infoWinOpen[idx] = true
        this.currentMidx = `sensor-${idx}`
      }
      console.log(this.infoWinOpen)
    }
  }
}
</script>
<style>
</style>
