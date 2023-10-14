<template lang="pug">
#myMap.fillScreen
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { polygonToCells, cellToBoundary, cellToLatLng, getHexagonAreaAvg, UNITS} from 'h3-js'
let map, hexLayer;

const GeoUtils = {
	EARTH_RADIUS_METERS: 6371000,

	degreesToRadians: (d) => d * Math.PI / 180,

	getDistanceOnEarthInMeters: (lat1, lon1, lat2, lon2) => {
		const lat1Rad  = GeoUtils.degreesToRadians(lat1);
		const lat2Rad  = GeoUtils.degreesToRadians(lat2);
		const lonDelta = GeoUtils.degreesToRadians(lon2 - lon1);
		const x = Math.sin(lat1Rad) * Math.sin(lat2Rad) +
			Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.cos(lonDelta);
		return GeoUtils.EARTH_RADIUS_METERS * Math.acos(Math.max(Math.min(x, 1), -1));
	}
};

const h3BoundsToPolygon = (lngLatH3Bounds) => {
	lngLatH3Bounds.push(lngLatH3Bounds[0]); // "close" the polygon
	return lngLatH3Bounds;
};
export default {
	data(){
		return{
			searchH3Id: undefined,
			gotoLatLon: undefined,
			actualSize:8,
			centerGeo:[54.20141722170296,37.635814342635875]
		}
	},
	methods: {
		computeAverageEdgeLengthInMeters: function(vertexLocations) {
			let totalLength = 0;
			let edgeCount = 0;
			for (let i = 1; i < vertexLocations.length; i++) {
				const [fromLat, fromLng] = vertexLocations[i - 1];
				const [toLat, toLng] = vertexLocations[i];
				const edgeDistance = GeoUtils.getDistanceOnEarthInMeters(fromLat, fromLng, toLat, toLng);
				totalLength += edgeDistance;
				edgeCount++;
			}
			return totalLength / edgeCount;
		},
		updateMapDisplay: function() {
			if (hexLayer) {
				hexLayer.remove();
			}

			hexLayer = L.layerGroup().addTo(map);

			const { _southWest: sw, _northEast: ne} = map.getBounds();

			const boundsPolygon =[
				[ sw.lat, sw.lng ],
				[ ne.lat, sw.lng ],
				[ ne.lat, ne.lng ],
				[ sw.lat, ne.lng ],
				[ sw.lat, sw.lng ],
			];
			//9 - от центра до угла 200м

			const h3s = polygonToCells(boundsPolygon,this.actualSize);

			for (const h3id of h3s) {

				const polygonLayer = L.layerGroup().addTo(hexLayer);

				const h3Bounds = cellToBoundary(h3id);
				const averageEdgeLength = this.computeAverageEdgeLengthInMeters(h3Bounds);

				const h3Polygon = L.polygon(h3BoundsToPolygon(h3Bounds))
					.on('click', () => {console.log(`Координаты точки: ${cellToLatLng(h3id)}`)})
					.bindTooltip(`
						ID: <b>${ h3id }</b>
						<br />
						Длина ребра (m): <b>${ averageEdgeLength.toLocaleString() }</b>
						<br />
						Площадь (km^2): <b>${getHexagonAreaAvg(this.actualSize,UNITS.km2).toFixed(3)} </b>
						<br />
					`)
					.addTo(polygonLayer);

				// less SVG, otherwise perf is bad
				if (Math.random() > 0.8) {
					let svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
					svgElement.setAttribute('xmlns', "http://www.w3.org/2000/svg");
					svgElement.setAttribute('viewBox', "0 0 200 200");
					svgElement.innerHTML = `<text x="20" y="70" class="h3Text">${h3id}</text>`;
					let svgElementBounds = h3Polygon.getBounds();
					L.svgOverlay(svgElement, svgElementBounds).addTo(polygonLayer);
				}
			}
		},
	},

	mounted() {
		document.addEventListener("DOMContentLoaded", () => {
			map = L.map('myMap');

			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				minZoom: 12,
				maxNativeZoom: 15,
				maxZoom: 15,
				attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
			}).addTo(map);
			L.layerGroup([]).addTo(map);


			map.setView(this.centerGeo, 14);
			map.on("zoomend", this.updateMapDisplay);
			map.on("moveend", this.updateMapDisplay);

			this.updateMapDisplay();
		})
	}
};
</script>

<style scoped>
	.fillScreen {
		width: 1050px;
		height: 620px;
		margin: auto;
	}
	.h3Text {
		font-size: 16pt;
		font-weight: bold;
	}
</style>