import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
const bundled = 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1123-915-0_26.1123.915.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe';
const python = process.env.KETUVI_PYTHON || (existsSync(bundled) ? bundled : process.platform === 'win32' ? 'python' : 'python3');
const result = spawnSync(python,['scripts/build_site.py', ...process.argv.slice(2)],{ stdio:'inherit' });
if (result.error) console.error('Configurez KETUVI_PYTHON avec un Python disposant de Pillow.');
process.exitCode = result.status ?? 1;
