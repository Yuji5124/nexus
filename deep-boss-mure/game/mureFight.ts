import type {Point} from './arenaFight';
const distance=(a:Point,b:Point):number=>Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
function segmentDistance(p:Point,a:Point,b:Point):number{
  const d={x:b.x-a.x,y:b.y-a.y,z:b.z-a.z},size=d.x*d.x+d.y*d.y+d.z*d.z;
  const t=size?Math.max(0,Math.min(1,((p.x-a.x)*d.x+(p.y-a.y)*d.y+(p.z-a.z)*d.z)/size)):0;
  return distance(p,{x:a.x+d.x*t,y:a.y+d.y*t,z:a.z+d.z*t});
}
export type MurePhase='drift'|'gather'|'stream'|'molt';
export const MURE_CYCLE=16;
/**
 * 4,500m「誰もいない王（ムレ）」の検証用の仮ルール。HP・時間・射程・ダメージはすべて仮の値で、仕様ではない。
 * 通常探索や保存データから独立している。Three.js・DOMへの依存なし。
 * 流れ: 漂泳 → 魚群の集合 (予兆。狙いは直前に固定) → 奔流 (翼から魚の帯が走る) → 脱皮 (輪郭を脱いで作り直す。隙あり)。
 */
export class MureFight {
  player:Point={x:0,y:30,z:100};
  anchor:Point={x:0,y:40,z:115};
  bossPos:Point={x:0,y:6,z:-40};
  aim:Point={x:0,y:30,z:100};
  hp=8;maxHp=8;maxBossHp=70;bossHp=70;time=0;selected=0;invulnerable=false;
  attackCooldown=0;hurtCooldown=0;dodgeTime=0;dodgeCooldown=0;
  readonly tether=200;readonly ceiling=130;readonly streamLength=190;readonly streamRadius=6.5;
  weaponLevels:readonly number[]=[0,0,0];
  private lastHitCycle=-1;
  constructor(){this.reset();}
  get won():boolean{return this.bossHp===0;}
  get lost():boolean{return this.hp===0;}
  get cycle():number{return Math.floor(this.time/MURE_CYCLE);}
  get cycleTime():number{return this.time%MURE_CYCLE;}
  /** 奔流を出す翼 (0: 左, 1: 右)。周期ごとに交互。 */
  get side():0|1{return this.cycle%2===0?1:0;}
  get phase():MurePhase{const t=this.cycleTime;return t<2.5?'drift':t<8?'gather':t<9.4?'stream':'molt';}
  /** 魚が奔流へ集まる度合い 0..1 (予兆の間にゆっくり増え、奔流の終わりから薄れる)。 */
  get streamAmount():number{const t=this.cycleTime;if(t<2.5)return 0;if(t<8)return (t-2.5)/5.5*.85;if(t<9.4)return 1;return Math.max(0,1-(t-9.4)/1.2);}
  /** 脱皮の度合い 0..1 (魚が輪郭から離れて戻る山形)。 */
  get shedAmount():number{const t=this.cycleTime;return t<9.4?0:Math.min(1,(t-9.4)/6.6);}
  reset():void{
    this.player={x:0,y:30,z:100};this.aim={x:0,y:30.65,z:100};this.hp=this.maxHp;this.bossHp=this.maxBossHp;this.time=0;this.selected=0;
    this.attackCooldown=0;this.hurtCooldown=0;this.dodgeTime=0;this.dodgeCooldown=0;this.lastHitCycle=-1;
  }
  move(x:number,y:number,z:number,dt:number):void{
    if(this.won||this.lost)return;
    const len=Math.max(1,Math.hypot(x,y,z)),speed=this.dodgeTime>0?42:17;
    const next={x:this.player.x+x/len*speed*dt,y:Math.max(.1,Math.min(this.ceiling,this.player.y+y/len*speed*dt)),z:this.player.z+z/len*speed*dt};
    const d=distance(next,this.anchor);
    if(d>this.tether){const k=this.tether/d;next.x=this.anchor.x+(next.x-this.anchor.x)*k;next.y=this.anchor.y+(next.y-this.anchor.y)*k;next.z=this.anchor.z+(next.z-this.anchor.z)*k;}
    this.player=next;
  }
  dodge():void{if(!this.won&&!this.lost&&this.dodgeCooldown<=0){this.dodgeTime=.4;this.dodgeCooldown=1.1;}}
  /** surfaceDistance: 最も近い発光マーカーまでの距離。近接 5.5m、アクセルの射撃は 58m。脱皮中は +1。 */
  hitBoss(surfaceDistance:number):boolean{
    if(this.won||this.lost||this.attackCooldown>0)return false;
    this.attackCooldown=this.selected===1?.3:.4;
    if(surfaceDistance>(this.selected===1?58:5.5))return false;
    this.bossHp=Math.max(0,this.bossHp-((this.selected===2?3:2)+(this.weaponLevels[this.selected]??0)*.5+(this.phase==='molt'?1:0)));return true;
  }
  heal():void{this.hp=this.maxHp;this.hurtCooldown=1.2;}
  damage(amount:number):void{
    if(this.won||this.lost||this.invulnerable||this.hurtCooldown>0||this.dodgeTime>0)return;
    this.hp=Math.max(0,this.hp-amount);this.hurtCooldown=1;
  }
  tick(dt:number):void{
    if(this.won||this.lost)return;
    this.time+=dt;this.attackCooldown=Math.max(0,this.attackCooldown-dt);this.hurtCooldown=Math.max(0,this.hurtCooldown-dt);
    this.dodgeTime=Math.max(0,this.dodgeTime-dt);this.dodgeCooldown=Math.max(0,this.dodgeCooldown-dt);
    // 奔流の直前 (6.5秒) まで狙いを追い、その後は固定。横か上下へ動けば避けられる。
    if(this.cycleTime<6.5)this.aim={...this.player,y:this.player.y+.65};
  }
  /** origin: 奔流を出す翼の先の世界座標。描く帯と同じ始点・終点 (origin→aim 方向、streamLength) で判定する。 */
  streamEnd(origin:Point):Point{const d=distance(origin,this.aim),k=this.streamLength/Math.max(1,d);return {x:origin.x+(this.aim.x-origin.x)*k,y:origin.y+(this.aim.y-origin.y)*k,z:origin.z+(this.aim.z-origin.z)*k};}
  checkStrike(origin:Point):void{
    if(this.won||this.lost||this.phase!=='stream'||this.lastHitCycle===this.cycle)return;
    if(segmentDistance({...this.player,y:this.player.y+.65},origin,this.streamEnd(origin))<this.streamRadius){this.damage(2);this.lastHitCycle=this.cycle;}
  }
}
