#!/usr/bin/env node

/**
 * 安装 Python 依赖的脚本
 * 在 npm install 时自动运行
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 检测 Python 命令
function getPythonCommand() {
  const commands = ['python3', 'python'];
  
  for (const cmd of commands) {
    try {
      const result = execSync(`${cmd} --version`, {
        stdio: 'pipe',
        encoding: 'utf-8'
      });
      
      const version = result || '';
      const match = version.match(/Python (\d+)\.(\d+)/);
      if (match) {
        const major = parseInt(match[1]);
        const minor = parseInt(match[2]);
        if (major === 3 && minor >= 10) {
          return cmd;
        }
      }
    } catch (e) {
      // 忽略错误，继续尝试
    }
  }
  
  return null;
}

// 检测 pip 命令
function getPipCommand(pythonCmd) {
  const pipCommands = ['pip3', 'pip'];
  
  for (const cmd of pipCommands) {
    try {
      execSync(`${cmd} --version`, { stdio: 'pipe' });
      return cmd;
    } catch (e) {
      // 忽略错误
    }
  }
  
  // 尝试使用 python -m pip
  try {
    execSync(`${pythonCmd} -m pip --version`, { stdio: 'pipe' });
    return `${pythonCmd} -m pip`;
  } catch (e) {
    return null;
  }
}

// 主安装函数
function installDependencies() {
  console.log('正在检查 Python 环境...');
  
  const pythonCmd = getPythonCommand();
  
  if (!pythonCmd) {
    console.warn('⚠️  警告: 未找到 Python 3.10+');
    console.warn('⚠️  请安装 Python 3.10 或更高版本: https://www.python.org/downloads/');
    console.warn('⚠️  跳过 Python 依赖安装');
    return;
  }
  
  console.log(`✓ 找到 Python: ${pythonCmd}`);
  
  const pipCmd = getPipCommand(pythonCmd);
  
  if (!pipCmd) {
    console.warn('⚠️  警告: 未找到 pip');
    console.warn('⚠️  请安装 pip 后手动运行: pip install -r requirements.txt');
    return;
  }
  
  console.log(`✓ 找到 pip: ${pipCmd}`);
  
  const rootDir = path.resolve(__dirname, '..');
  const requirementsFile = path.join(rootDir, 'requirements.txt');
  
  if (!fs.existsSync(requirementsFile)) {
    console.warn('⚠️  警告: 找不到 requirements.txt');
    return;
  }
  
  console.log('正在安装 Python 依赖...');
  
  try {
    // 尝试安装依赖
    execSync(`${pipCmd} install -r "${requirementsFile}"`, {
      stdio: 'inherit',
      cwd: rootDir
    });
    
    console.log('✓ Python 依赖安装完成');
  } catch (error) {
    console.warn('⚠️  警告: Python 依赖安装失败');
    console.warn('⚠️  请手动运行: pip install -r requirements.txt');
  }
}

// 运行安装
try {
  installDependencies();
} catch (error) {
  console.error('安装过程出错:', error.message);
  // 不中断安装过程
}
