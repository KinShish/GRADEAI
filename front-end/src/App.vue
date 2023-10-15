<template lang="pug">
img.bgImage(src="/img/hero.jpg")
.headerMobile
	img(src="/img/logo.svg")
.titleBlock Сервис для
	span оценки
	| достаточности
	br
	| и удобства городской
	br
	| инфраструктуры
.mainContent
	.title Выберите город что бы начать анализ
	form.formAnal(@submit.stop.prevent="$_searchCity(0)")
		.form-group
			label Город
			VueSelect(:options="arrayCity" v-model="arrayMaps[0].form.city" placeholder="Выберите город")
				template(#no-options="{ search }")
					span(v-if="search.length>=2") Ничего не найдено
					span(v-else) Начните искать
		//.form-group
			label Выберите точность
			VueSelect(:options="arraySize" v-model="arrayMap[0].form.sizeText" placeholder="Выберите точность" @option:selected="$_select_size(index)" :searchable="false")
		button.btn(type="submit" :disabled="arrayMaps[0].spinner")
			PraiSpinner(v-if="arrayMaps[0].spinner")
			span(v-else) Начать анализ
	.title.moreMarginTitle(v-if="arrayMaps[0].loaded") Результаты поиска
	PraiMap(v-if="arrayMaps[0].loaded" :idMap="`mapNumber-${0}-${arrayMaps[0].tab}`" @changeTab="arrayMaps[0].tab=$event;arrayMaps[0].key++"
		:key="arrayMaps[0].key" :data="arrayMaps[0].data" :keyUpdate="arrayMaps[0].key" :size="arrayMaps[0].form.size" :tab="arrayMaps[0].tab" :city="arrayMaps[0].form.city")
	//.btn.compareBtn(v-if="arrayMaps[0].loaded" @click="$_compare") Сравнить
	.compareBlock(v-if="showCompare")
		.title Выберите вторую точку для сравнения
		form.formAnal(@submit.stop.prevent="$_searchCity(1)")
			.form-group
				label Город
				VueSelect(:options="arrayCity" v-model="arrayMaps[1].form.city" placeholder="Выберите город")
					template(#no-options="{ search }")
						span(v-if="search.length>=2") Ничего не найдено
						span(v-else) Начните искать
			button.btn(type="submit" :disabled="arrayMaps[1].spinner")
				PraiSpinner(v-if="arrayMaps[1].spinner")
				span(v-else) Сравнить
		.listCompare(v-if="arrayMaps[1].loaded")
			.blockCompare(v-for="item of arrayMaps")
				.title {{item.form.city}}
				.statusWithImg
					img(src="/img/good.svg")
					| Положительные точки
				.greyBlockPercent {{item.data.good}}
		.btn.compareBtn(v-if="arrayMaps[1].loaded" @click="$_compare_reset") Сравнить другую точку
</template>

<script>
import "leaflet/dist/leaflet.css";
import PraiMap from "@/components/PraiMap.vue";
import axios from 'axios';
import VueSelect from "vue-select";
import PraiSpinner from "@/components/PraiSpinner.vue";
export default {
	data(){
		return{
			showCompare:false,
			colorStatus:['#FF6F6F','#FF9345','#FFDA19','#179273'],
			arrayCity:['Екатеринбург','Тула','Тверь'],
			arraySize:['1000 кв.','400 кв.', '100 кв.'],
			arraySizeNumber:{'1000 кв.':8,'400 кв.':9,'100 кв.':10},
			arrayMaps: {
				0: {
					form: {city: 'Екатеринбург', size: 8, sizeText:'1000 кв.'},
					loaded: false,
					spinner: false,
					key:0,
					tab:0,
					data:{}
				}
			},
		}
	},
	components:{PraiSpinner, PraiMap,VueSelect},
	methods:{
		async requestFnc(method,url,formData){
			const res = await axios({method, url: 'http://192.168.0.107:3000/api/'+url, data:formData})
			if(res.status === 200){
				return res.data
			}else return false
		},
		$_compare_reset(){
			this.showCompare = false
			delete this.arrayMaps[1]
			this.$nextTick(()=>{
				this.$_compare()
			})
		},
		$_compare(){
			this.arrayMaps[1]={
				form: {city: 'Тула', size: 8, sizeText:'1000 кв.'},
				loaded: false,
				spinner: false,
				key:0,
				tab:0,
				data:{}
			}
			this.showCompare = true
		},
		async $_searchCity(index){
			if(this.arrayMaps[index].form.city){
				this.arrayMaps[index].spinner = true
				this.arrayMaps[index].loaded = false
				const res = await this.requestFnc('POST','get/city',{name:this.arrayMaps[index].form.city})
				if(res){
					this.arrayMaps[index].data=[]
					Object.keys(res).forEach(key=>{
						this.arrayMaps[index].data.push(res[key])
						this.arrayMaps[index].data.at(-1).name = key
					})
					this.arrayMaps[index].key = new Date().getTime()
					this.arrayMaps[index].loaded = true
					this.arrayMaps[index].spinner = false
					window.scroll(0, 200)
				}
			}
		},
		$_select_size(index){
			this.arrayMaps[index].form.size = this.arraySizeNumber[this.arrayMaps[index].form.sizeText]
		}
	}
};
</script>

<style>
	@font-face {
		font-family: Inter;
		src: url('@/css/fonts/Inter.woff2') format('woff2'), url('@/css/fonts/Inter.ttf') format('truetype');
	}
	body{
		padding-bottom: 100px;
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
		max-width: 1100px;
		width: 100%;
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
		max-width: 1100px;
		width: 100%;
		margin: auto;
	}
	.title{
		margin-bottom: 20px;
		color: #040034;
		font-size: 20px;
		font-weight: 700;
		line-height: 20px;
	}
	.formAnal{
		display: flex;
		justify-content: space-between;
		column-gap: 20px;
		align-items: flex-end;
	}
	.formAnal .form-group{
		flex: 1;
	}
	.formAnal .btn{
		width: 180px;
	}
	.moreMarginTitle{
		margin-top: 40px;
	}
	.compareBtn{
		width: 180px;
		margin: 20px auto;
	}
	.listCompare{
		display: flex;
		column-gap: 20px;
	}
	.blockCompare{
		padding: 20px;
		border-radius: 10px;
		border: 2px solid #179273;
		background: #FFF;
		flex: 1;
		margin-top: 40px;
	}
	.greyBlockPercent{
		color: #040034;
		font-size: 30px;
		font-weight: 700;
		line-height: 30px;
	}
	.statusWithImg{
		display: flex;
		column-gap: 9px;
		color: #179273;
		font-size: 16px;
		font-weight: 700;
		line-height: 24px;
		margin-bottom: 25px;
	}
	@media (max-width: 1100px) {
		.titleBlock{
			max-width: calc(100% - 40px);
		}
	}
	.headerMobile{
		display: none;
	}
	@media (max-width: 768px) {
		.titleBlock{
			font-size: 18px;
			line-height: 25px;
		}
		.title{
			font-size: 13px;
			line-height: 20px;
		}
		.formAnal{
			flex-wrap: wrap;
		}
		.formAnal .btn{
			flex-basis: 100%;
			margin-top: 20px;
		}
		.titleBlock{
			padding-top: 85px;
			padding-bottom: 30px;
		}
		.mainContent{
			box-shadow: none;
			padding: 20px;
		}
		.title{
			font-size: 20px;
			line-height: 20px;
		}
		.headerMobile{
			position: fixed;
			top: 0;
			width: 100%;
			left: 0;
			height: 50px;
			display: flex;
			align-items: center;
			justify-content: center;
			background-color: white;
		}
	}
</style>