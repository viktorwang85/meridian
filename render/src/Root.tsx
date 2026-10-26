import React from 'react';
import {AbsoluteFill,Composition,Sequence,interpolate,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import type {Caption} from '@remotion/captions';

type Broll={source:string;from:number;duration:number};
type Props={experiment_id:string;source:string;hook:string;cta:string;duration:number;caption_style:string;captions:Caption[];broll:Broll[];first_frame_card:boolean;subtle_zoom:boolean};
const asset=(s:string)=>/^https?:\/\//.test(s)?s:staticFile(s);
export const Reel:React.FC<Props>=(p)=>{
 const frame=useCurrentFrame();const {fps}=useVideoConfig();
 const caption=p.captions.filter(c=>frame/fps*1000>=c.startMs&&frame/fps*1000<c.endMs).map(c=>c.text).join(' ');
 return <AbsoluteFill style={{background:'#112b25',color:'#f7efdc',fontFamily:'Arial, sans-serif'}}>
  {p.source?<Video src={asset(p.source)} premountFor={fps} style={{width:'100%',height:'100%',objectFit:'cover',scale:p.subtle_zoom?interpolate(frame,[0,p.duration*fps],[1,1.06],{extrapolateRight:'clamp'}):1}}/>:<AbsoluteFill style={{background:'linear-gradient(150deg,#183f32,#0e201d)',padding:100,justifyContent:'center',fontSize:62}}>RETURN TO BALI<br/><span style={{color:'#e5bd80',fontSize:110}}>Season 01</span><p style={{fontSize:36}}>Добавьте исходник в props JSON</p></AbsoluteFill>}
  {p.broll.map((b,i)=><Sequence key={i} from={Math.round(b.from*fps)} durationInFrames={Math.round(b.duration*fps)} premountFor={fps}><Video src={asset(b.source)} muted premountFor={fps} style={{width:'100%',height:'100%',objectFit:'cover'}}/></Sequence>)}
  {p.first_frame_card&&<Sequence durationInFrames={Math.round(2*fps)} premountFor={fps}><AbsoluteFill style={{background:'#0c1e19',padding:'300px 90px',justifyContent:'center',fontSize:76,lineHeight:1.15}}><span style={{fontSize:28,color:'#e5bd80',marginBottom:40}}>{p.experiment_id} / RETURN TO BALI</span>{p.hook}</AbsoluteFill></Sequence>}
  {caption&&<div style={{position:'absolute',left:90,right:160,bottom:380,fontSize:58,lineHeight:1.25,textAlign:'center',background:p.caption_style==='minimal'?'transparent':'rgba(0,0,0,.7)',padding:20,borderRadius:14,whiteSpace:'pre-wrap'}}>{caption}</div>}
  <Sequence from={Math.max(0,Math.round((p.duration-3)*fps))} durationInFrames={Math.round(3*fps)} premountFor={fps}><div style={{position:'absolute',left:90,right:160,bottom:300,background:'#e5bd80',color:'#112b25',padding:30,fontSize:52,borderRadius:15}}>{p.cta}</div></Sequence>
 </AbsoluteFill>
};
export const Root=()=> <Composition id="BaliReel" component={Reel} durationInFrames={900} fps={30} width={1080} height={1920}
 defaultProps={{experiment_id:'BALI-0001',source:'',hook:'Я прожил на Бали 11 лет. Теперь возвращаюсь с Настей.',cta:'Напиши БАЛИ — расскажу о формате',duration:30,caption_style:'default',captions:[{text:'Я хочу показать Насте свой Бали.',startMs:2500,endMs:6000,timestampMs:null,confidence:null}],broll:[],first_frame_card:true,subtle_zoom:false}}
 calculateMetadata={({props})=>{if(![15,30,45,60].includes(props.duration))throw Error('duration must be 15, 30, 45 or 60');return {durationInFrames:Math.round(props.duration*30)};}}/>;
