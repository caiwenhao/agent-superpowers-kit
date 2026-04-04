---
name: dev-qa
description: |
  全面测试：启动前后端服务，浏览器测试 + 接口验证 + 日志分析 + 数据库检查。
  发现问题自动修复并重新验证，循环直到全部通过。
  Use when: "测试", "QA", "全面测试", "test everything",
  "run qa", "跑一下测试", "验证功能"
argument-hint: "[测试 URL 或服务启动说明]"
---

# /dev-qa - 全面测试 + 自动修复

启动前后端服务，进行浏览器测试 + 接口验证 + 日志分析 + 数据库检查。
发现问题自动修复，循环直到全部通过。

## 输入

<test_context> #$ARGUMENTS </test_context>

## 流程

### Step 1: 确认测试环境

检查项目配置文件（CLAUDE.md, package.json, Makefile, docker-compose.yml 等），
自动检测前后端启动命令。

如果无法自动检测，用 AskUserQuestion 询问：
> 请提供以下信息：
> - 前端启动命令（如 `npm run dev`）
> - 后端启动命令（如 `go run main.go`）
> - 测试 URL（如 `http://localhost:3000`）
> - 数据库类型和连接方式（如有）

### Step 2: 启动服务

在后台启动前端和后端服务：

```bash
# 后端（示例）
cd backend && go run main.go &
BACKEND_PID=$!

# 前端（示例）
cd frontend && npm run dev &
FRONTEND_PID=$!

# 等待服务就绪
sleep 5
curl -sf http://localhost:3000 > /dev/null && echo "前端就绪"
curl -sf http://localhost:8080/health > /dev/null && echo "后端就绪"
```

根据项目实际配置调整命令。

### Step 3: 全面测试

并行执行以下测试：

#### 3a. 浏览器测试 (gstack-qa)

使用 Skill tool 调用 `gstack-qa`，进行浏览器端测试：
- 页面渲染验证
- 交互功能测试
- UI 回归检查
- 发现问题自动修复

#### 3b. 接口验证 (Superpowers)

使用 Agent tool 启动 `bug-reproduction-validator` (Superpower)：
- 验证 API 接口的请求/响应
- 检查错误处理
- 验证边界条件

#### 3c. 日志分析

检查服务运行日志：
```bash
# 检查后端日志中的 error/panic/warning
grep -i "error\|panic\|warning\|fatal" /tmp/backend.log
```

#### 3d. 数据库检查（如适用）

检查数据库状态：
- 表结构是否正确
- 数据完整性
- migration 是否成功

### Step 4: 问题修复循环

如果任何测试发现问题：
1. 汇总所有问题
2. 自动修复代码
3. 重启服务
4. 重新运行失败的测试
5. 循环直到全部通过（最多 5 轮）

### Step 5: 停止服务 + 输出

测试全部通过后：
1. 停止后台服务
2. 输出测试结果总结

告诉用户：

> 全面测试通过。
> - 浏览器测试: ✓ {N} 项通过
> - 接口验证: ✓ {N} 项通过
> - 日志检查: ✓ 无异常
> - 数据库检查: ✓ 正常
>
> 下一步：
> - `/dev-accept` - 进入人工验收
