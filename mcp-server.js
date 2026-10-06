import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const apiBase = process.env.NEXUS_API_URL || "http://127.0.0.1:4173";

async function api(path, options) {
  const response = await fetch(`${apiBase}${path}`, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `NEXUS API returned ${response.status}`);
  return data;
}

function result(value) {
  return { content: [{ type: "text", text: JSON.stringify(value, null, 2) }] };
}

const server = new McpServer({ name: "nexus", version: "0.1.0" });

server.registerTool("search_assets", {
  description: "Search NEXUS assets. Results are ranked CC0/free/GLB first.",
  inputSchema: {
    q: z.string().optional().describe("Text or tag query"),
    type: z.enum(["all", "model", "material", "texture", "hdri", "pack"]).optional(),
    cc0: z.boolean().optional().describe("Only return CC0 assets"),
    glb: z.boolean().optional().describe("Only return GLB assets")
  }
}, async ({ q = "", type = "all", cc0 = false, glb = false }) => {
  const params = new URLSearchParams({ q, type, free: "true", cc0: String(cc0), glb: String(glb) });
  return result(await api(`/api/search?${params}`));
});

server.registerTool("get_asset", {
  description: "Get full metadata and usage information for one NEXUS asset.",
  inputSchema: { id: z.string() }
}, async ({ id }) => result(await api(`/api/assets/${encodeURIComponent(id)}`)));

server.registerTool("download_asset", {
  description: "Download a provider asset into the NEXUS Library. Existing files are reused.",
  inputSchema: { id: z.string() }
}, async ({ id }) => result(await api(`/api/assets/${encodeURIComponent(id)}/download`, { method: "POST" })));

server.registerTool("list_library", {
  description: "List assets stored in the local NEXUS Library.",
  inputSchema: {}
}, async () => result(await api("/api/library")));

server.registerTool("list_projects", {
  description: "List explicitly registered Project Bridge destinations.",
  inputSchema: {}
}, async () => result(await api("/api/projects")));

server.registerTool("send_to_project", {
  description: "Send an asset to a registered project destination after path safety checks.",
  inputSchema: { id: z.string(), project: z.string() }
}, async ({ id, project }) => result(await api(`/api/assets/${encodeURIComponent(id)}/send`, {
  method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ project })
})));

server.registerTool("search_local_assets", {
  description: "Search only assets already stored in the local NEXUS Library.",
  inputSchema: { q: z.string().optional() }
}, async ({ q = "" }) => {
  const library = await api("/api/library");
  const needle = q.toLowerCase();
  return result(library.filter((asset) => !needle || `${asset.name} ${asset.provider} ${(asset.tags || []).join(" ")}`.toLowerCase().includes(needle)));
});

const transport = new StdioServerTransport();
await server.connect(transport);
