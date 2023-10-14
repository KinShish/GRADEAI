<template lang="pug">
//img.bgImage(src="/img/hero.jpg")
//.titleBlock Сервис для
	span оценки
	| достаточности
	br
	| и удобства городской
	br
	| инфраструктуры
.mainContent
	.title Выберите город что бы начать анализ
	PraiMap
</template>

<script>
import "leaflet/dist/leaflet.css";
import PraiMap from "@/components/PraiMap.vue";
export default {
	data(){
		return{

		}
	},
	components:{PraiMap},
};
</script>

<style>
	.leaflet-control-attribution{
		display: none;
	}
	@font-face {
		font-family: Inter;
		src: url('@/css/fonts/Inter.woff2') format('woff2'), url('@/css/fonts/Inter.ttf') format('truetype');
	}
	*{
		font-family: Inter;
	}
	.bgImage{
		position: absolute;
		width: 100%;
		z-index: -1;
		top: 0;
	}
	.titleBlock{
		color: white;
		padding: 130px 0 70px 0;
		font-size: 55px;
		line-height: 70px;
		flex-direction: row;
		width: 1100px;
		font-weight: 700;
		margin: 0 auto;
	}
	.titleBlock span{
		color: #179273;
		margin: 0 8px;
	}
	.mainContent{
		padding: 30px;
		border-radius: 20px;
		background: #FFF;
		box-shadow: 10px 40px 50px 0 rgba(80, 80, 80, 0.40);
		width: 1100px;
		margin: auto;
	}
	.title{
		margin-bottom: 20px;
		color: #040034;
		font-size: 20px;
		font-weight: 700;
		line-height: 20px;
	}
</style>