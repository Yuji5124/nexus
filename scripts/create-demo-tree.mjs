import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import fs from 'node:fs/promises';
globalThis.FileReader=class {
  readAsArrayBuffer(blob){blob.arrayBuffer().then(value=>{this.result=value;this.onloadend?.();});}
  readAsDataURL(blob){blob.arrayBuffer().then(value=>{this.result='data:'+blob.type+';base64,'+Buffer.from(value).toString('base64');this.onloadend?.();});}
};
const scene=new THREE.Scene();
const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.12,.18,1.4,6),new THREE.MeshStandardMaterial({color:0x76513a}));
trunk.position.y=.7;scene.add(trunk);
const crown=new THREE.Mesh(new THREE.IcosahedronGeometry(.9,1),new THREE.MeshStandardMaterial({color:0x65a84b,flatShading:true}));
crown.position.y=1.7;scene.add(crown);
const buffer=await new GLTFExporter().parseAsync(scene,{binary:true});
await fs.mkdir('assets/nature/tree',{recursive:true});
await fs.writeFile('assets/nature/tree/demo_tree.glb',Buffer.from(buffer));
console.log('Created original procedural demo tree GLB.');
