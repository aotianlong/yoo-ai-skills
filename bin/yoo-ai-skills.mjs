#!/usr/bin/env node
/**
 * yoo-ai-skills — 将仓库 skills/ 下的技能分发到 Cursor / Claude Code / Codex 默认目录。
 */
import { cp, lstat, mkdir, readdir, readFile, rm, symlink, unlink } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");
const SKILLS_DIR = join(PROJECT_ROOT, "skills");
const TARGETS_FILE = join(PROJECT_ROOT, "config", "targets.defaults.json");

function printHelp() {
  console.log(`yoo-ai-skills — 统一 skills 分发工具

用法:
  yoo-ai-skills list
  yoo-ai-skills sync [选项]

sync 选项:
  --targets <a,b>   仅同步列出目标，默认全部。可选: cursor, claude, codex
  --skill <name>    仅同步某一个 skill 目录名
  --method <m>      copy（复制）或 symlink（符号链接），默认 symlink
  --dry-run         仅打印将要执行的操作
  --help            显示本帮助

说明:
  源目录为本仓库 skills/<slug>/，每个子目录需包含 SKILL.md。
  目标路径见 config/targets.defaults.json。
`);
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const out = { cmd: null, targets: null, skill: null, method: "symlink", dryRun: false };
  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    out.cmd = "help";
    return out;
  }
  out.cmd = args.shift();

  while (args.length > 0) {
    const a = args.shift();
    if (a === "--help" || a === "-h") out.cmd = "help";
    else if (a === "--dry-run") out.dryRun = true;
    else if (a === "--targets" && args.length) out.targets = args.shift().split(",").map((s) => s.trim()).filter(Boolean);
    else if (a === "--skill" && args.length) out.skill = args.shift().trim();
    else if (a === "--method" && args.length) {
      const m = args.shift();
      if (m !== "copy" && m !== "symlink") throw new Error(`--method 只能是 copy 或 symlink，收到: ${m}`);
      out.method = m;
    } else {
      throw new Error(`未知参数: ${a}`);
    }
  }
  return out;
}

async function loadTargetsMeta() {
  const raw = await readFile(TARGETS_FILE, "utf8");
  const j = JSON.parse(raw);
  return j.targets;
}

function resolveRoot(pathTpl) {
  return pathTpl.replace("<home>", homedir());
}

async function listSkillSlugs() {
  const entries = await readdir(SKILLS_DIR, { withFileTypes: true });
  const slugs = [];
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const skillPath = join(SKILLS_DIR, e.name, "SKILL.md");
    try {
      await lstat(skillPath);
      slugs.push(e.name);
    } catch {
      // 跳过无 SKILL.md 的目录
    }
  }
  return slugs.sort();
}

async function ensureRemoved(linkPath, dryRun) {
  try {
    const st = await lstat(linkPath);
    if (dryRun) {
      console.log(`  [dry-run] 将删除现有: ${linkPath}`);
      return;
    }
    if (st.isSymbolicLink()) await unlink(linkPath);
    else await rm(linkPath, { recursive: true, force: true });
  } catch (e) {
    if (e?.code !== "ENOENT") throw e;
  }
}

async function publishOneSkill(sourceDir, destDir, method, dryRun) {
  if (dryRun) {
    console.log(`  [dry-run] ${method}: ${sourceDir} -> ${destDir}`);
    return;
  }
  await mkdir(dirname(destDir), { recursive: true });
  await ensureRemoved(destDir, false);
  if (method === "copy") await cp(sourceDir, destDir, { recursive: true });
  else {
    const absSource = resolve(sourceDir);
    await symlink(absSource, destDir, "dir");
  }
}

async function cmdList() {
  const slugs = await listSkillSlugs();
  if (slugs.length === 0) {
    console.log(`(skills 目录下暂无有效 skill，需在 ${SKILLS_DIR}/<slug>/SKILL.md)`);
    return;
  }
  console.log("可用 skills:");
  for (const s of slugs) console.log(`  - ${s}`);
}

async function cmdSync(opts) {
  const targetsMeta = await loadTargetsMeta();
  const allNames = ["cursor", "claude", "codex"];
  let names = opts.targets?.length ? opts.targets : allNames;
  const unknown = names.filter((n) => !targetsMeta[n]);
  if (unknown.length) throw new Error(`未知 targets: ${unknown.join(", ")}；可用: ${allNames.join(", ")}`);

  const slugs = opts.skill ? [opts.skill] : await listSkillSlugs();
  if (opts.skill && !slugs.includes(opts.skill)) {
    throw new Error(`skill 不存在或缺少 SKILL.md: ${opts.skill}`);
  }

  console.log(`源: ${SKILLS_DIR}`);
  console.log(`方式: ${opts.method}${opts.dryRun ? " (dry-run)" : ""}`);

  for (const targetName of names) {
    const root = resolveRoot(targetsMeta[targetName].skillsRoot);
    console.log(`\n→ ${targetName}: ${root}`);
    for (const slug of slugs) {
      const src = join(SKILLS_DIR, slug);
      const dest = join(root, slug);
      console.log(`  · ${slug}`);
      await publishOneSkill(src, dest, opts.method, opts.dryRun);
    }
  }
  console.log("\n完成。");
}

async function main() {
  let opts;
  try {
    opts = parseArgs(process.argv);
  } catch (e) {
    console.error(e.message || e);
    process.exitCode = 1;
    return;
  }
  if (opts.cmd === "help" || !opts.cmd) {
    printHelp();
    return;
  }
  try {
    if (opts.cmd === "list") await cmdList();
    else if (opts.cmd === "sync") await cmdSync(opts);
    else {
      console.error(`未知命令: ${opts.cmd}`);
      printHelp();
      process.exitCode = 1;
    }
  } catch (e) {
    console.error(e.message || e);
    process.exitCode = 1;
  }
}

main();
