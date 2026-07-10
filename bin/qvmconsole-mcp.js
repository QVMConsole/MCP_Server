#!/usr/bin/env node

/**
 * QVMConsole MCP Server 启动脚本
 * 这个脚本会启动 Python MCP Server
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 检测 Python 命令
function getPythonCommand() {
  const commands = ['python3', 'python'];
  
  for (const cmd of commands) {
    try {
      const result = require('child_process').spawnSync(cmd, ['--version'], {
        stdio: 'pipe',
        encoding: 'utf-8'
      });
      
      if (result.status === 0) {
        const version = result.stdout || result.stderr;
        // 检查是否是 Python 3.10+
        const match = version.match(/Python (\d+)\.(\d+)/);
        if (match) {
          const major = parseInt(match[1]);
          const minor = parseInt(match[2]);
          if (major === 3 && minor >= 10) {
            return cmd;
          }
        }
      }
    } catch (e) {
      // 忽略错误，继续尝试下一个命令
    }
  }
  
  return null;
}

// 解析环境变量配置
function parseEnvConfig() {
  // 从 stdin 读取 MCP 配置（如果有的话）
  // Claude Desktop 会通过环境变量传递配置
  const env = process.env;
  
  // 支持通过环境变量配置
  if (env.QVMC_BASE_URL || env.QVMCONSOLE_BASE_URL) {
    return {
      QVMC_BASE_URL: env.QVMC_BASE_URL || env.QVMCONSOLE_BASE_URL,
      QVMC_API_KEY_ID: env.QVMC_API_KEY_ID || env.QVMCONSOLE_API_KEY_ID,
      QVMC_API_KEY: env.QVMC_API_KEY || env.QVMCONSOLE_API_KEY,
      QVMC_TIMEOUT: env.QVMC_TIMEOUT || env.QVMCONSOLE_TIMEOUT,
      QVMC_VERIFY_SSL: env.QVMC_VERIFY_SSL || env.QVMCONSOLE_VERIFY_SSL
    };
  }
  
  return {};
}

// 主函数
function main() {
  const pythonCmd = getPythonCommand();
  
  if (!pythonCmd) {
    console.error('错误: 未找到 Python 3.10 或更高版本');
    console.error('请安装 Python 3.10+ 后再试: https://www.python.org/downloads/');
    process.exit(1);
  }
  
  // 获取项目根目录
  const rootDir = path.resolve(__dirname, '..');
  const serverScript = path.join(rootDir, 'src', 'server.py');
  
  // 检查服务器脚本是否存在
  if (!fs.existsSync(serverScript)) {
    console.error(`错误: 找不到服务器脚本 ${serverScript}`);
    process.exit(1);
  }
  
  // 解析环境变量配置
  const envConfig = parseEnvConfig();
  
  // 启动 Python MCP Server
  const pythonProcess = spawn(pythonCmd, [serverScript], {
    stdio: 'inherit',
    cwd: rootDir,
    env: {
      ...process.env,
      ...envConfig
    }
  });
  
  // 处理进程退出
  pythonProcess.on('exit', (code) => {
    process.exit(code || 0);
  });
  
  // 处理错误
  pythonProcess.on('error', (err) => {
    console.error('启动 Python 进程时出错:', err.message);
    process.exit(1);
  });
  
  // 处理终止信号
  process.on('SIGINT', () => {
    pythonProcess.kill('SIGINT');
  });
  
  process.on('SIGTERM', () => {
    pythonProcess.kill('SIGTERM');
  });
}

// 运行
main();
