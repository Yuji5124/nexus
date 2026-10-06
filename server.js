import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.join(path.dirname(fileURLToPath(import.meta.url)),'dist');
const mime={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.glb':'model/gltf-binary','.gltf':'model/gltf+json'};
const port=Number(process.env.PORT || 4173);
http.createServer(async(req,res)=>{
  try{
    const url=new URL(req.url,'http://localhost'), relative=decodeURIComponent(url.pathname).replace(/^\/nexus\//,'/');
    const file=path.resolve(root,'.'+(relative==='/'?'/index.html':relative));
    if(!file.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
    const bytes=await fs.readFile(file);res.writeHead(200,{'content-type':mime[path.extname(file)] || 'application/octet-stream'});res.end(bytes);
  }catch{res.writeHead(404);res.end('Not found. Run npm run build before preview.');}
}).listen(port,process.env.HOST || '127.0.0.1',()=>console.log('NEXUS development preview on port '+port));
