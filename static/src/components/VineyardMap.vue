<template>
  <div>
    <GmapMap
      v-if="google && vineyard"
      :center="center"
      :zoom="17"
      map-type-id="satellite"
      style="width: 100%; height: 400px"
      >
        <gmap-info-window :options="infoOptions" :position="infoWindowPos" :opened="infoWinOpen" @closeclick="infoWinOpen=false">
          <sensor-modal
            v-if="vineyard.sensors"
            v-for="sensor in vineyard.sensors"
            :key="sensor.id"
            :sensor="sensor"/>
        </gmap-info-window>
      <GmapMarker
        :key="index"
        v-for="(m, index) in markers"
        :position="m.position"
        :clickable="true"
        :draggable="false"
        @click="toggleInfoWindow(m, index)"
        />
    </GmapMap>
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
      infoWinOpen: false,
      currentMidx: null,
      infoOptions: {
        pixelOffset: {
          width: 0,
          height: -35
        }
      }
    }
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
            infoText: this.vineyard.sensors[i].description
          })
        }
      }
      return markers
    },
    toggleInfoWindow: function(marker, idx) {
      this.infoWindowPos = marker.position
      this.infoContent = marker.infoText

      if (this.currentMidx === idx) {
        this.infoWinOpen = !this.infoWinOpen
      } else {
        this.infoWinOpen = true
        this.currentMidx = idx
      }
    }
  }
}
</script>
<style>
</style>
