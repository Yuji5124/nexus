#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { constants } from 'node:fs';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { searchAssets } from './src/search.js';
const indexUrl=process.env.NEXUS_INDEX_URL || 'https://raw.githubusercontent.com/Yuji5124/nexus/main/data/assets.json';
const projectRoot=await fs.realpath(process.env.NEXUS_PROJECT_ROOT || process.cwd());
async function index() {const r=await fetch(indexUrl);if(!r.ok) throw new Error('GitHub index HTTP '+r.status);return r.json();}
async function asset(id) {const a=(await index()).find(a=>a.id===id);if(!a) throw new Error('Asset not found');return a;}
const result=v=>({content:[{type:'text',text:JSON.stringify(v,null,2)}]});
const server=new McpServer({name:'nexus-github',version:'0.2.0'});
server.registerTool('search_assets',{description:'Search the GitHub NEXUS asset index, including license and online URLs.',inputSchema:{query:z.string().optional(),category:z.string().optional(),tags:z.array(z.string()).optional(),format:z.string().optional(),maxTriangles:z.number().positive().optional(),animated:z.boolean().optional()}},async f=>result(searchAssets(await index(),f)));
server.registerTool('get_asset',{description:'Read metadata from GitHub.',inputSchema:{assetId:z.string()}},async({assetId})=>result(await asset(assetId)));
server.registerTool('get_asset_url',{description:'Return the GitHub Pages and raw URLs.',inputSchema:{assetId:z.string()}},async({assetId})=>{const a=await asset(assetId);return result({assetId,url:a.previewUrl,rawUrl:a.rawUrl,license:a.license});});
server.registerTool('list_assets',{description:'List GitHub assets by category.',inputSchema:{category:z.string().optional()}},async f=>result(searchAssets(await index(),f)));
server.registerTool('find_similar_assets',{description:'Find candidates by shared tags and category.',inputSchema:{assetId:z.string()}},async({assetId})=>{const all=await index(),a=all.find(a=>a.id===assetId);if(!a) throw new Error('Asset not found');return result(all.filter(b=>b.id!==a.id).map(b=>({...b,similarity:(b.tags||[]).filter(t=>(a.tags||[]).includes(t)).length+(b.category===a.category?1:0)})).filter(b=>b.similarity>0).sort((a,b)=>b.similarity-a.similarity).slice(0,20));});
server.registerTool('download_asset',{description:'Download from GitHub into the consuming game project. Existing files are never overwritten.',inputSchema:{assetId:z.string(),targetDirectory:z.string()}},async({assetId,targetDirectory})=>{
  const a=await asset(assetId);
  const target=path.resolve(projectRoot,targetDirectory);
  if(target!==projectRoot&&!target.startsWith(projectRoot+path.sep)) throw new Error('Destination must be inside NEXUS_PROJECT_ROOT');
  let ancestor=target;
  while(true){try{const real=await fs.realpath(ancestor);if(real!==projectRoot&&!real.startsWith(projectRoot+path.sep)) throw new Error('Destination symlink escapes project');break;}catch(e){if(e.code!=='ENOENT')throw e;ancestor=path.dirname(ancestor);}}
  const extension=path.extname(a.path).toLowerCase();
  if(!['.glb','.png','.jpg','.jpeg','.webp','.obj','.fbx'].includes(extension))throw new Error('Multi-file glTF requires downloading its dependency bundle; use GLB.');
  const url=new URL(a.rawUrl);if(url.origin!=='https://raw.githubusercontent.com'||!url.pathname.startsWith('/Yuji5124/nexus/'))throw new Error('Unexpected asset source');
  const response=await fetch(url);if(!response.ok)throw new Error('Download HTTP '+response.status);
  const data=Buffer.from(await response.arrayBuffer());
  await fs.mkdir(target,{recursive:true});
  const destination=path.join(target,path.basename(a.path));await fs.writeFile(destination,data,{flag:'wx'});
  return result({assetId,destination,license:a.license,author:a.author,sourceUrl:a.sourceUrl});
});
await server.connect(new StdioServerTransport());
