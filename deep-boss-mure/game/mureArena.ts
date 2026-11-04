import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {InputManager} from '../input/manager';
import {CrabAnimator} from '../fx/crabAnim';
import {makeRng} from '../gen/rng';
import {playBgm} from '../audio/bgm';
import {distance,type Point} from './arenaFight';
import {MureFight} from './mureFight';
import {DEBUG_PARTY,DEBUG_LABELS,debugBattleUrl} from './catalog';
import {mountDebugTools} from './tools';

/** 4,500m「誰もいない王（ムレ）」の検証用の仮戦闘。HP・ダメージ・時間はすべて仮。肉体は無く、約4万匹の小魚の配置だけで姿をつくる。 */
const $=<T extends HTMLElement>(id:string)=>document.getElementById(id) as T;
$('retry').after($('continue'));
if(new URLSearchParams(location.search).get('debug')!=='1')history.replaceState(null,'',debugBattleUrl('mure'));
const fight=new MureFight(),input=new InputManager();
document.title='誰もいない王（ムレ）｜3人ボス戦テスト';$('boss-name').textContent='誰もいない王（ムレ）';$('depth').textContent='4,500m / 仮の戦闘テスト（検証用の仮実装）';
const renderer=new THREE.WebGLRenderer({canvas:$<HTMLCanvasElement>('game'),antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.toneMapping=THREE.ACESFilmicToneMapping;
const BG=0x5b7686;
const scene=new THREE.Scene();scene.background=new THREE.Color(BG);scene.fog=new THREE.FogExp2(BG,.0018);
const camera=new THREE.PerspectiveCamera(55,1,.5,2500),composer=new EffectComposer(renderer);
composer.addPass(new RenderPass(scene,camera));composer.addPass(new UnrealBloomPass(new THREE.Vector2(1,1),.3,.5,.9));composer.addPass(new OutputPass());
scene.add(new THREE.HemisphereLight(0xe6f0f4,0x6f8a97,2.2));
const sun=new THREE.DirectionalLight(0xfff0dc,2.2);sun.position.set(80,200,120);scene.add(sun);
const floor=new THREE.Mesh(new THREE.CircleGeometry(520,80),new THREE.MeshStandardMaterial({color:0xaebcc2,roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.04;scene.add(floor);
const rng=makeRng(4500),pearl=new THREE.MeshStandardMaterial({color:0xdfe6e8,roughness:.8,emissive:0x2a3338});
for(let i=0;i<46;i++){const a=rng()*Math.PI*2,r=260+rng()*220,h=10+rng()*60;const m=new THREE.Mesh(new THREE.CylinderGeometry(2.4,3.6,h,8),pearl);m.position.set(Math.cos(a)*r,h/2,Math.sin(a)*r);scene.add(m);}
const dustGeo=new THREE.BufferGeometry(),dp=new Float32Array(2600*3);for(let i=0;i<dp.length;i+=3){dp[i]=(rng()-.5)*700;dp[i+1]=rng()*160;dp[i+2]=(rng()-.5)*700;}
dustGeo.setAttribute('position',new THREE.BufferAttribute(dp,3));const dust=new THREE.Points(dustGeo,new THREE.PointsMaterial({color:0xffffff,size:.5,opacity:.5,transparent:true,depthWrite:false}));scene.add(dust);
const boat=new THREE.Group();boat.position.set(fight.anchor.x,fight.anchor.y,fight.anchor.z);scene.add(boat);
const boss=new THREE.Group();boss.position.set(fight.bossPos.x,fight.bossPos.y,fight.bossPos.z);scene.add(boss);
const actors:THREE.Group[]=[],animators:CrabAnimator[]=[];
const lamp=new THREE.PointLight(0xdff6ff,120,40);scene.add(lamp);
const cableGeometry=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]);const cable=new THREE.Line(cableGeometry,new THREE.LineBasicMaterial({color:0x80dfe5,transparent:true,opacity:.7}));cable.frustumCulled=false;scene.add(cable);
const marker=new THREE.Mesh(new THREE.SphereGeometry(3,16,10),new THREE.MeshBasicMaterial({color:0xffe4a5,wireframe:true,transparent:true,opacity:.85}));scene.add(marker);
const aimLineGeometry=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]);
const aimLine=new THREE.Line(aimLineGeometry,new THREE.LineBasicMaterial({color:0xffba6a,transparent:true,opacity:.6}));aimLine.frustumCulled=false;scene.add(aimLine);
const shotGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]);const shot=new THREE.Line(shotGeo,new THREE.LineBasicMaterial({color:0xffdc9d}));shot.frustumCulled=false;scene.add(shot);
let shotTime=0,ready=false,paused=false,menuCursor=0,prevAxis=0,cameraReady=false,announced=false,hitTime=0;
const hitLocal=new THREE.Vector3();
const vector=(p:Point)=>new THREE.Vector3(p.x,p.y,p.z);
const line=(g:THREE.BufferGeometry,a:THREE.Vector3,b:THREE.Vector3)=>{const p=g.attributes.position as THREE.BufferAttribute;p.setXYZ(0,a.x,a.y,a.z);p.setXYZ(1,b.x,b.y,b.z);p.needsUpdate=true;};

// ---- 魚群 (InstancedBufferGeometry)。位置・向き・部位は boss_mure_school.bin (float32 x 11)。
const STRIDE=11;
interface Target{name:string;local:THREE.Vector3;wing:0|1|-1}
const targets:Target[]=[];
const uniforms={uTime:{value:0},uStream:{value:0},uShed:{value:0},uHitT:{value:0},uStreamO:{value:new THREE.Vector3()},uStreamD:{value:new THREE.Vector3(0,0,1)},uHitP:{value:new THREE.Vector3()}};
const wingFlap=(x:number,t:number)=>{const k=Math.abs(x)/110;return Math.sin(t*.9)*k*k*14;};
function buildSchool(buffer:ArrayBuffer):void{
  const f=new Float32Array(buffer),n=f.length/STRIDE;
  const fishGeo=new THREE.InstancedBufferGeometry();
  const l=1.6,w=l*.16,h=l*.22;
  const v=[0,0,l*.55,0,0,-l*.5,w,0,0,-w,0,0,0,h,0,0,-h*.8,0];
  const idx=[0,2,4,0,4,3,0,3,5,0,5,2,1,4,2,1,3,4,1,5,3,1,2,5];
  fishGeo.setAttribute('position',new THREE.BufferAttribute(new Float32Array(v),3));fishGeo.setIndex(idx);
  const pos=new Float32Array(n*3),dir=new Float32Array(n*3),meta=new Float32Array(n*4);
  const acc=new Map<string,{s:THREE.Vector3;n:number}>();
  const add=(k:string,x:number,y:number,z:number)=>{const a=acc.get(k)??{s:new THREE.Vector3(),n:0};a.s.add(new THREE.Vector3(x,y,z));a.n++;acc.set(k,a);};
  for(let i=0;i<n;i++){
    const o=i*STRIDE;pos.set([f[o],f[o+1],f[o+2]],i*3);dir.set([f[o+3],f[o+4],f[o+5]],i*3);
    const part=f[o+7],u=f[o+6];meta.set([part,f[o+8],f[o+9],f[o+10]],i*4);
    if(part===0)add('head',f[o],f[o+1],f[o+2]);else if(part===1)add('crown',f[o],f[o+1],f[o+2]);
    else if(part===3&&u>.85)add('chest',f[o],f[o+1],f[o+2]);
    else if(part===4&&u>.85)add('wingL',f[o],f[o+1],f[o+2]);else if(part===5&&u>.85)add('wingR',f[o],f[o+1],f[o+2]);
  }
  for(const [name,wing] of [['head',-1],['crown',-1],['chest',-1],['wingL',0],['wingR',1]] as const){const a=acc.get(name);if(a)targets.push({name,local:a.s.divideScalar(a.n),wing});}
  fishGeo.setAttribute('aPos',new THREE.InstancedBufferAttribute(pos,3));fishGeo.setAttribute('aDir',new THREE.InstancedBufferAttribute(dir,3));fishGeo.setAttribute('aMeta',new THREE.InstancedBufferAttribute(meta,4));
  fishGeo.instanceCount=n;
  const mat=new THREE.ShaderMaterial({uniforms,side:THREE.DoubleSide,
    vertexShader:`attribute vec3 aPos;attribute vec3 aDir;attribute vec4 aMeta;
uniform float uTime,uStream,uShed,uHitT;uniform vec3 uStreamO,uStreamD,uHitP;
varying vec3 vCol;varying float vShade;
mat3 basis(vec3 f){vec3 r=abs(f.y)>.99?vec3(1.,0.,0.):normalize(cross(vec3(0.,1.,0.),f));vec3 u=cross(f,r);return mat3(r,u,f);}
void main(){
  float part=aMeta.x,ph=aMeta.y,sz=aMeta.z;vec3 p=aPos,d=normalize(aDir);
  p+=vec3(sin(uTime*.7+ph*40.),cos(uTime*.6+ph*31.),sin(uTime*.5+ph*23.))*.8;
  if(part>3.5&&part<5.5){float k=abs(p.x)/110.;p.y+=sin(uTime*.9)*k*k*14.;}
  if(part>5.5&&part<6.5){p.x+=sin(uTime*1.1-p.z*.06)*clamp(-p.z/100.,0.,1.)*8.;}
  if(part<6.5&&ph<.3){p+=normalize(vec3(sin(ph*97.),sin(ph*57.)*.6+.2,cos(ph*71.)))*sin(3.14159*uShed)*22.*(.4+ph);}
  if(part>6.5){
    vec3 s1=normalize(cross(uStreamD,vec3(0.,1.,0.)));vec3 s2=cross(uStreamD,s1);
    vec3 sp=uStreamO+uStreamD*(fract(uTime*.35+ph)*190.)+s1*sin(ph*113.)*5.+s2*sin(ph*71.)*5.;
    p=mix(p,sp,uStream);d=normalize(mix(d,uStreamD,uStream));
  }
  float hh=uHitT*smoothstep(16.,0.,distance(p,uHitP));p+=normalize(p-uHitP+vec3(.001))*hh*10.;
  mat3 B=basis(d);vec3 pw=p+B*(position*sz*1.25);
  vec3 n=normalize(mat3(modelMatrix)*(B*normalize(position+vec3(0.,.1,0.))));
  vShade=.55+.45*max(0.,dot(n,normalize(vec3(.4,.8,.5))));
  vec3 c=aMeta.w<.5?vec3(.86,.9,.95):aMeta.w<1.5?vec3(.98,.94,.89):aMeta.w<2.5?vec3(.97,.8,.42):vec3(.95,.72,.8);
  vCol=c*(1.+.35*(part>6.5?uStream:0.));
  gl_Position=projectionMatrix*viewMatrix*modelMatrix*vec4(pw,1.);}`,
    fragmentShader:`varying vec3 vCol;varying float vShade;void main(){gl_FragColor=vec4(vCol*vShade*1.1+vCol*.12,1.);}`});
  const mesh=new THREE.Mesh(fishGeo,mat);mesh.frustumCulled=false;boss.add(mesh);
}
const tools=mountDebugTools({restart:reset,heal:()=>{fight.heal();announced=false;$('resume').hidden=false;pause(false);}});
function pause(value:boolean):void{paused=value;$('pause').hidden=!value;menuCursor=0;}
function reset():void{fight.reset();pause(false);cameraReady=false;announced=false;shotTime=0;hitTime=0;for(const a of animators)a.reset();$('resume').hidden=false;}
async function load():Promise<void>{
  try{
    const loader=new GLTFLoader();
    const [bin,sub,...crew]=await Promise.all([fetch('/boss_mure_school.bin').then(r=>r.arrayBuffer()),loader.loadAsync('/submarine.glb'),...DEBUG_PARTY.map(c=>loader.loadAsync(c==='shrimp'?'/shrimp_redpink.glb':`/${c}.glb`))]);
    buildSchool(bin);boat.add(sub.scene);
    crew.forEach(g=>{const root=new THREE.Group();root.add(g.scene);scene.add(root);actors.push(root);animators.push(new CrabAnimator(g.scene,g.animations));});
    ready=true;reset();
  }catch(error){console.error(error);$('phase').textContent='読み込めませんでした。再挑戦してください。';}
}
const targetWorld=(t:Target):THREE.Vector3=>{const p=t.local.clone();if(t.wing>=0)p.y+=wingFlap(p.x,uniforms.uTime.value);return p.add(boss.position);};
function streamOrigin():THREE.Vector3{const t=targets.find(x=>x.wing===fight.side);return t?targetWorld(t):boss.position.clone();}
function attack():void{
  if(fight.attackCooldown>0||fight.won||fight.lost)return;
  const from=vector(fight.player).add(new THREE.Vector3(0,.65,0));
  let best=Infinity,target=targets[0];for(const t of targets){const d=from.distanceTo(targetWorld(t))-6;if(d<best){best=d;target=t;}}
  animators[fight.selected]?.trigger('Attack');
  if(target&&fight.hitBoss(best)){line(shotGeo,from,targetWorld(target));shotTime=.13;hitLocal.copy(target.local);uniforms.uHitP.value.copy(hitLocal);hitTime=1;marker.material.color.setHex(0xffffff);}
}
function update(dt:number):void{
  const s=input.state,old={...fight.player};
  fight.invulnerable=tools.invulnerable();
  if(s.pressed.has('map')&&!fight.won&&!fight.lost)fight.selected=(fight.selected+1)%3;
  if(s.pressed.has('dodge'))fight.dodge();
  fight.move(s.move.x,(s.down.has('ascend')?1:0)-(s.down.has('descend')?1:0),-s.move.y,dt);
  fight.tick(dt);
  uniforms.uTime.value+=dt;hitTime=Math.max(0,hitTime-dt*1.6);uniforms.uHitT.value=hitTime;
  uniforms.uShed.value=fight.won?0:fight.shedAmount;
  const origin=streamOrigin(),aim=vector(fight.aim),end=vector(fight.streamEnd(origin)),dir=end.clone().sub(origin).normalize();
  uniforms.uStream.value=fight.won?0:fight.streamAmount;uniforms.uStreamO.value.copy(origin).sub(boss.position);uniforms.uStreamD.value.copy(dir);
  fight.checkStrike(origin);
  const moving=distance(old,fight.player)>.005,heading=moving?Math.atan2(fight.player.x-old.x,fight.player.z-old.z):Math.atan2(boss.position.x-fight.player.x,boss.position.z-fight.player.z);
  let follower=0;actors.forEach((actor,i)=>{const target=vector(fight.player);if(i!==fight.selected){follower++;target.x+=(follower===1?-1:1)*2.7;target.z+=3.2;target.y=Math.max(.1,target.y-.2);}actor.position.lerp(target,1-Math.exp(-dt*12));actor.rotation.y=heading;actor.visible=fight.hurtCooldown<=0||Math.floor(fight.hurtCooldown*15)%2===0;animators[i].setBase(moving?(fight.dodgeTime>0?'Dash':'Swim'):'Idle');animators[i].update(dt);});
  if(s.down.has('attack'))attack();
  aimLine.visible=fight.phase==='gather'&&!fight.won;line(aimLineGeometry,origin,end);
  void aim;
  let nearest=targets[0],nd=Infinity;for(const t of targets){const d=targetWorld(t).distanceTo(vector(fight.player));if(d<nd){nd=d;nearest=t;}}
  marker.visible=!fight.won&&!!nearest;if(nearest)marker.position.copy(targetWorld(nearest));marker.material.color.lerp(new THREE.Color(0xffe4a5),dt*5);
  line(cableGeometry,boat.position,vector(fight.player).add(new THREE.Vector3(0,.5,0)));lamp.position.copy(vector(fight.player)).y+=4;
  shotTime=Math.max(0,shotTime-dt);shot.visible=shotTime>0;dust.rotation.y+=dt*.002;
  $('boss-hp-fill').style.width=`${fight.bossHp/fight.maxBossHp*100}%`;$('boss-health').textContent=`${fight.bossHp} / ${fight.maxBossHp}（仮）`;
  $('player-health').textContent=`HP ${fight.hp} / ${fight.maxHp}${fight.invulnerable?' · 無敵ON':''}`;
  $('party').textContent=DEBUG_LABELS.map((n,i)=>`${i===fight.selected?'▶ ':''}${n}`).join('   ');
  $('phase').textContent=fight.won?'静かに散った':({drift:'漂泳',gather:'魚群が翼へ集まる',stream:'奔流',molt:'脱皮 · 輪郭を脱ぐ（隙あり）'})[fight.phase];
  $('hint').textContent=fight.phase==='gather'?'光の線が止まったら、横か上下へ回避':fight.phase==='molt'?'脱皮の間は攻撃が通りやすい':fight.selected===1?'Y 射撃 · 発光マーカーのある群れへ自動照準':'発光マーカーのある群れへ近づいて攻撃 · Rで浮上';
  $('tether').textContent=`光の糸 ${Math.round(distance(fight.player,fight.anchor))} / ${fight.tether}m`;
  $('controls').textContent=s.pad.kind==='profile'?'十字キー 移動 · R / L 浮上 / 下降 · Y 攻撃 · A 回避 · Select 仲間切替 · Start 一時停止':'矢印/WASD 移動 · E/Q 浮上/下降 · J 攻撃 · Space 回避 · M 仲間切替 · Esc 一時停止';
  if((fight.won||fight.lost)&&!announced){announced=true;$('pause-title').textContent=fight.won?'静かに散った':'力尽きました';$('resume').hidden=true;pause(true);menuCursor=0;}
}
function updateCamera(dt:number):void{
  const p=vector(fight.player),at=p.clone().lerp(boss.position.clone().add(new THREE.Vector3(0,60,0)),.55);
  const wanted=p.clone().add(new THREE.Vector3(45,28,85));
  if(!cameraReady){camera.position.copy(wanted);cameraReady=true;}else camera.position.lerp(wanted,1-Math.exp(-dt*3));camera.lookAt(at);
}
$('resume').addEventListener('click',()=>pause(false));$('retry').addEventListener('click',reset);
function resize():void{const w=innerWidth,h=innerHeight;renderer.setSize(w,h,false);composer.setPixelRatio(renderer.getPixelRatio());composer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}addEventListener('resize',resize);resize();
let last=performance.now();renderer.setAnimationLoop(now=>{const dt=Math.min(.04,(now-last)/1000);last=now;const s=input.update();
  if(ready&&s.pressed.has('pause')&&!fight.won&&!fight.lost){$('pause-title').textContent='一時停止';pause(!paused);}
  if(ready&&paused){const buttons=[$('resume'),$('retry'),$('continue'),$('return')].filter(b=>!b.hidden);const y=s.move.y;if(Math.abs(y)>.6&&Math.abs(prevAxis)<=.6)menuCursor=(menuCursor+(y>0?-1:1)+buttons.length)%buttons.length;menuCursor%=buttons.length;buttons.forEach((b,i)=>b.classList.toggle('selected',i===menuCursor));if(s.pressed.has('attack'))buttons[menuCursor].click();prevAxis=y;}
  else if(ready){update(dt);updateCamera(dt);}composer.render();});
void load();playBgm('guardian');
